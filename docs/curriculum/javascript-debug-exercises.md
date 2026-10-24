# JavaScript Debug Exercises

A RAG-training corpus of 300 JavaScript debugging exercises. Corrected code is editorial material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: runtime behavior, type reasoning, state, contracts, collections, async control flow, security boundaries, and complexity


## JS-E-001: loose equality

- Difficulty: Easy
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check1(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check1(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check1(0) === 'empty'); console.assert(check1('0') === 'filled');
```


## JS-E-002: truthiness and zero

- Difficulty: Easy
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label2(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label2(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label2(0) === 'present'); console.assert(label2(undefined) === 'missing');
```


## JS-E-003: array mutation

- Difficulty: Easy
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add3(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add3(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source3 = [1]; const result3 = add3(source3, 2); console.assert(source3.length === 1);
```


## JS-E-004: for in versus for of

- Difficulty: Easy
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum4(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum4(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum4([2, 3]) === 5);
```


## JS-E-005: default parameter

- Difficulty: Easy
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name5(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name5(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name5(null) === 'guest'); console.assert(name5(undefined) === 'guest');
```


## JS-E-006: reduce without identity

- Difficulty: Easy
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total6(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total6(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total6([]) === 0); console.assert(total6([2, 3]) === 5);
```


## JS-E-007: loop capture

- Difficulty: Easy
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks7(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks7(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs7 = callbacks7(['a', 'b']); console.assert(fs7[0]() === 'a');
```


## JS-E-008: prototype pollution

- Difficulty: Easy
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has8(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has8(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object8 = Object.create({hidden: true}); console.assert(has8(object8, 'hidden') === false);
```


## JS-E-009: missing await

- Difficulty: Easy
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load9() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load9() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load9() and assert the parsed value; reject a non-OK response.
```


## JS-E-010: unvalidated JSON

- Difficulty: Easy
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user10(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user10(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user10('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-E-011: loose equality

- Difficulty: Easy
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check11(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check11(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check11(0) === 'empty'); console.assert(check11('0') === 'filled');
```


## JS-E-012: truthiness and zero

- Difficulty: Easy
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label12(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label12(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label12(0) === 'present'); console.assert(label12(undefined) === 'missing');
```


## JS-E-013: array mutation

- Difficulty: Easy
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add13(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add13(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source13 = [1]; const result13 = add13(source13, 2); console.assert(source13.length === 1);
```


## JS-E-014: for in versus for of

- Difficulty: Easy
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum14(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum14(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum14([2, 3]) === 5);
```


## JS-E-015: default parameter

- Difficulty: Easy
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name15(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name15(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name15(null) === 'guest'); console.assert(name15(undefined) === 'guest');
```


## JS-E-016: reduce without identity

- Difficulty: Easy
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total16(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total16(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total16([]) === 0); console.assert(total16([2, 3]) === 5);
```


## JS-E-017: loop capture

- Difficulty: Easy
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks17(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks17(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs17 = callbacks17(['a', 'b']); console.assert(fs17[0]() === 'a');
```


## JS-E-018: prototype pollution

- Difficulty: Easy
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has18(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has18(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object18 = Object.create({hidden: true}); console.assert(has18(object18, 'hidden') === false);
```


## JS-E-019: missing await

- Difficulty: Easy
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load19() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load19() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load19() and assert the parsed value; reject a non-OK response.
```


## JS-E-020: unvalidated JSON

- Difficulty: Easy
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user20(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user20(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user20('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-E-021: loose equality

- Difficulty: Easy
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check21(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check21(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check21(0) === 'empty'); console.assert(check21('0') === 'filled');
```


## JS-E-022: truthiness and zero

- Difficulty: Easy
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label22(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label22(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label22(0) === 'present'); console.assert(label22(undefined) === 'missing');
```


## JS-E-023: array mutation

- Difficulty: Easy
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add23(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add23(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source23 = [1]; const result23 = add23(source23, 2); console.assert(source23.length === 1);
```


## JS-E-024: for in versus for of

- Difficulty: Easy
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum24(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum24(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum24([2, 3]) === 5);
```


## JS-E-025: default parameter

- Difficulty: Easy
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name25(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name25(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name25(null) === 'guest'); console.assert(name25(undefined) === 'guest');
```


## JS-E-026: reduce without identity

- Difficulty: Easy
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total26(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total26(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total26([]) === 0); console.assert(total26([2, 3]) === 5);
```


## JS-E-027: loop capture

- Difficulty: Easy
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks27(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks27(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs27 = callbacks27(['a', 'b']); console.assert(fs27[0]() === 'a');
```


## JS-E-028: prototype pollution

- Difficulty: Easy
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has28(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has28(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object28 = Object.create({hidden: true}); console.assert(has28(object28, 'hidden') === false);
```


## JS-E-029: missing await

- Difficulty: Easy
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load29() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load29() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load29() and assert the parsed value; reject a non-OK response.
```


## JS-E-030: unvalidated JSON

- Difficulty: Easy
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user30(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user30(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user30('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-E-031: loose equality

- Difficulty: Easy
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check31(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check31(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check31(0) === 'empty'); console.assert(check31('0') === 'filled');
```


## JS-E-032: truthiness and zero

- Difficulty: Easy
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label32(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label32(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label32(0) === 'present'); console.assert(label32(undefined) === 'missing');
```


## JS-E-033: array mutation

- Difficulty: Easy
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add33(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add33(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source33 = [1]; const result33 = add33(source33, 2); console.assert(source33.length === 1);
```


## JS-E-034: for in versus for of

- Difficulty: Easy
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum34(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum34(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum34([2, 3]) === 5);
```


## JS-E-035: default parameter

- Difficulty: Easy
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name35(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name35(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name35(null) === 'guest'); console.assert(name35(undefined) === 'guest');
```


## JS-E-036: reduce without identity

- Difficulty: Easy
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total36(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total36(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total36([]) === 0); console.assert(total36([2, 3]) === 5);
```


## JS-E-037: loop capture

- Difficulty: Easy
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks37(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks37(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs37 = callbacks37(['a', 'b']); console.assert(fs37[0]() === 'a');
```


## JS-E-038: prototype pollution

- Difficulty: Easy
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has38(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has38(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object38 = Object.create({hidden: true}); console.assert(has38(object38, 'hidden') === false);
```


## JS-E-039: missing await

- Difficulty: Easy
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load39() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load39() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load39() and assert the parsed value; reject a non-OK response.
```


## JS-E-040: unvalidated JSON

- Difficulty: Easy
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user40(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user40(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user40('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-E-041: loose equality

- Difficulty: Easy
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check41(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check41(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check41(0) === 'empty'); console.assert(check41('0') === 'filled');
```


## JS-E-042: truthiness and zero

- Difficulty: Easy
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label42(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label42(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label42(0) === 'present'); console.assert(label42(undefined) === 'missing');
```


## JS-E-043: array mutation

- Difficulty: Easy
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add43(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add43(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source43 = [1]; const result43 = add43(source43, 2); console.assert(source43.length === 1);
```


## JS-E-044: for in versus for of

- Difficulty: Easy
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum44(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum44(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum44([2, 3]) === 5);
```


## JS-E-045: default parameter

- Difficulty: Easy
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name45(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name45(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name45(null) === 'guest'); console.assert(name45(undefined) === 'guest');
```


## JS-E-046: reduce without identity

- Difficulty: Easy
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total46(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total46(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total46([]) === 0); console.assert(total46([2, 3]) === 5);
```


## JS-E-047: loop capture

- Difficulty: Easy
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks47(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks47(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs47 = callbacks47(['a', 'b']); console.assert(fs47[0]() === 'a');
```


## JS-E-048: prototype pollution

- Difficulty: Easy
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has48(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has48(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object48 = Object.create({hidden: true}); console.assert(has48(object48, 'hidden') === false);
```


## JS-E-049: missing await

- Difficulty: Easy
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load49() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load49() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load49() and assert the parsed value; reject a non-OK response.
```


## JS-E-050: unvalidated JSON

- Difficulty: Easy
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user50(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user50(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user50('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-E-051: loose equality

- Difficulty: Easy
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check51(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check51(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check51(0) === 'empty'); console.assert(check51('0') === 'filled');
```


## JS-E-052: truthiness and zero

- Difficulty: Easy
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label52(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label52(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label52(0) === 'present'); console.assert(label52(undefined) === 'missing');
```


## JS-E-053: array mutation

- Difficulty: Easy
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add53(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add53(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source53 = [1]; const result53 = add53(source53, 2); console.assert(source53.length === 1);
```


## JS-E-054: for in versus for of

- Difficulty: Easy
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum54(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum54(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum54([2, 3]) === 5);
```


## JS-E-055: default parameter

- Difficulty: Easy
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name55(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name55(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name55(null) === 'guest'); console.assert(name55(undefined) === 'guest');
```


## JS-E-056: reduce without identity

- Difficulty: Easy
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total56(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total56(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total56([]) === 0); console.assert(total56([2, 3]) === 5);
```


## JS-E-057: loop capture

- Difficulty: Easy
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks57(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks57(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs57 = callbacks57(['a', 'b']); console.assert(fs57[0]() === 'a');
```


## JS-E-058: prototype pollution

- Difficulty: Easy
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has58(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has58(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object58 = Object.create({hidden: true}); console.assert(has58(object58, 'hidden') === false);
```


## JS-E-059: missing await

- Difficulty: Easy
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load59() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load59() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load59() and assert the parsed value; reject a non-OK response.
```


## JS-E-060: unvalidated JSON

- Difficulty: Easy
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user60(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user60(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user60('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-E-061: loose equality

- Difficulty: Easy
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check61(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check61(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check61(0) === 'empty'); console.assert(check61('0') === 'filled');
```


## JS-E-062: truthiness and zero

- Difficulty: Easy
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label62(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label62(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label62(0) === 'present'); console.assert(label62(undefined) === 'missing');
```


## JS-E-063: array mutation

- Difficulty: Easy
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add63(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add63(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source63 = [1]; const result63 = add63(source63, 2); console.assert(source63.length === 1);
```


## JS-E-064: for in versus for of

- Difficulty: Easy
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum64(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum64(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum64([2, 3]) === 5);
```


## JS-E-065: default parameter

- Difficulty: Easy
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name65(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name65(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name65(null) === 'guest'); console.assert(name65(undefined) === 'guest');
```


## JS-E-066: reduce without identity

- Difficulty: Easy
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total66(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total66(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total66([]) === 0); console.assert(total66([2, 3]) === 5);
```


## JS-E-067: loop capture

- Difficulty: Easy
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks67(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks67(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs67 = callbacks67(['a', 'b']); console.assert(fs67[0]() === 'a');
```


## JS-E-068: prototype pollution

- Difficulty: Easy
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has68(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has68(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object68 = Object.create({hidden: true}); console.assert(has68(object68, 'hidden') === false);
```


## JS-E-069: missing await

- Difficulty: Easy
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load69() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load69() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load69() and assert the parsed value; reject a non-OK response.
```


## JS-E-070: unvalidated JSON

- Difficulty: Easy
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user70(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user70(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user70('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-E-071: loose equality

- Difficulty: Easy
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check71(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check71(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check71(0) === 'empty'); console.assert(check71('0') === 'filled');
```


## JS-E-072: truthiness and zero

- Difficulty: Easy
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label72(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label72(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label72(0) === 'present'); console.assert(label72(undefined) === 'missing');
```


## JS-E-073: array mutation

- Difficulty: Easy
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add73(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add73(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source73 = [1]; const result73 = add73(source73, 2); console.assert(source73.length === 1);
```


## JS-E-074: for in versus for of

- Difficulty: Easy
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum74(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum74(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum74([2, 3]) === 5);
```


## JS-E-075: default parameter

- Difficulty: Easy
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name75(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name75(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name75(null) === 'guest'); console.assert(name75(undefined) === 'guest');
```


## JS-E-076: reduce without identity

- Difficulty: Easy
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total76(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total76(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total76([]) === 0); console.assert(total76([2, 3]) === 5);
```


## JS-E-077: loop capture

- Difficulty: Easy
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks77(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks77(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs77 = callbacks77(['a', 'b']); console.assert(fs77[0]() === 'a');
```


## JS-E-078: prototype pollution

- Difficulty: Easy
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has78(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has78(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object78 = Object.create({hidden: true}); console.assert(has78(object78, 'hidden') === false);
```


## JS-E-079: missing await

- Difficulty: Easy
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load79() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load79() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load79() and assert the parsed value; reject a non-OK response.
```


## JS-E-080: unvalidated JSON

- Difficulty: Easy
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user80(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user80(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user80('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-E-081: loose equality

- Difficulty: Easy
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check81(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check81(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check81(0) === 'empty'); console.assert(check81('0') === 'filled');
```


## JS-E-082: truthiness and zero

- Difficulty: Easy
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label82(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label82(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label82(0) === 'present'); console.assert(label82(undefined) === 'missing');
```


## JS-E-083: array mutation

- Difficulty: Easy
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add83(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add83(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source83 = [1]; const result83 = add83(source83, 2); console.assert(source83.length === 1);
```


## JS-E-084: for in versus for of

- Difficulty: Easy
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum84(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum84(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum84([2, 3]) === 5);
```


## JS-E-085: default parameter

- Difficulty: Easy
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name85(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name85(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name85(null) === 'guest'); console.assert(name85(undefined) === 'guest');
```


## JS-E-086: reduce without identity

- Difficulty: Easy
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total86(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total86(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total86([]) === 0); console.assert(total86([2, 3]) === 5);
```


## JS-E-087: loop capture

- Difficulty: Easy
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks87(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks87(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs87 = callbacks87(['a', 'b']); console.assert(fs87[0]() === 'a');
```


## JS-E-088: prototype pollution

- Difficulty: Easy
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has88(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has88(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object88 = Object.create({hidden: true}); console.assert(has88(object88, 'hidden') === false);
```


## JS-E-089: missing await

- Difficulty: Easy
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load89() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load89() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load89() and assert the parsed value; reject a non-OK response.
```


## JS-E-090: unvalidated JSON

- Difficulty: Easy
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user90(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user90(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user90('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-E-091: loose equality

- Difficulty: Easy
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check91(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check91(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check91(0) === 'empty'); console.assert(check91('0') === 'filled');
```


## JS-E-092: truthiness and zero

- Difficulty: Easy
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label92(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label92(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label92(0) === 'present'); console.assert(label92(undefined) === 'missing');
```


## JS-E-093: array mutation

- Difficulty: Easy
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add93(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add93(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source93 = [1]; const result93 = add93(source93, 2); console.assert(source93.length === 1);
```


## JS-E-094: for in versus for of

- Difficulty: Easy
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum94(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum94(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum94([2, 3]) === 5);
```


## JS-E-095: default parameter

- Difficulty: Easy
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name95(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name95(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name95(null) === 'guest'); console.assert(name95(undefined) === 'guest');
```


## JS-E-096: reduce without identity

- Difficulty: Easy
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total96(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total96(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total96([]) === 0); console.assert(total96([2, 3]) === 5);
```


## JS-E-097: loop capture

- Difficulty: Easy
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks97(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks97(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs97 = callbacks97(['a', 'b']); console.assert(fs97[0]() === 'a');
```


## JS-E-098: prototype pollution

- Difficulty: Easy
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has98(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has98(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object98 = Object.create({hidden: true}); console.assert(has98(object98, 'hidden') === false);
```


## JS-E-099: missing await

- Difficulty: Easy
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load99() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load99() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load99() and assert the parsed value; reject a non-OK response.
```


## JS-E-100: unvalidated JSON

- Difficulty: Easy
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user100(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user100(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user100('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-M-001: loose equality

- Difficulty: Medium
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check1(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check1(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check1(0) === 'empty'); console.assert(check1('0') === 'filled');
```


## JS-M-002: truthiness and zero

- Difficulty: Medium
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label2(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label2(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label2(0) === 'present'); console.assert(label2(undefined) === 'missing');
```


## JS-M-003: array mutation

- Difficulty: Medium
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add3(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add3(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source3 = [1]; const result3 = add3(source3, 2); console.assert(source3.length === 1);
```


## JS-M-004: for in versus for of

- Difficulty: Medium
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum4(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum4(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum4([2, 3]) === 5);
```


## JS-M-005: default parameter

- Difficulty: Medium
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name5(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name5(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name5(null) === 'guest'); console.assert(name5(undefined) === 'guest');
```


## JS-M-006: reduce without identity

- Difficulty: Medium
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total6(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total6(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total6([]) === 0); console.assert(total6([2, 3]) === 5);
```


## JS-M-007: loop capture

- Difficulty: Medium
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks7(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks7(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs7 = callbacks7(['a', 'b']); console.assert(fs7[0]() === 'a');
```


## JS-M-008: prototype pollution

- Difficulty: Medium
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has8(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has8(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object8 = Object.create({hidden: true}); console.assert(has8(object8, 'hidden') === false);
```


## JS-M-009: missing await

- Difficulty: Medium
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load9() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load9() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load9() and assert the parsed value; reject a non-OK response.
```


## JS-M-010: unvalidated JSON

- Difficulty: Medium
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user10(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user10(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user10('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-M-011: loose equality

- Difficulty: Medium
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check11(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check11(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check11(0) === 'empty'); console.assert(check11('0') === 'filled');
```


## JS-M-012: truthiness and zero

- Difficulty: Medium
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label12(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label12(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label12(0) === 'present'); console.assert(label12(undefined) === 'missing');
```


## JS-M-013: array mutation

- Difficulty: Medium
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add13(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add13(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source13 = [1]; const result13 = add13(source13, 2); console.assert(source13.length === 1);
```


## JS-M-014: for in versus for of

- Difficulty: Medium
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum14(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum14(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum14([2, 3]) === 5);
```


## JS-M-015: default parameter

- Difficulty: Medium
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name15(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name15(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name15(null) === 'guest'); console.assert(name15(undefined) === 'guest');
```


## JS-M-016: reduce without identity

- Difficulty: Medium
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total16(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total16(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total16([]) === 0); console.assert(total16([2, 3]) === 5);
```


## JS-M-017: loop capture

- Difficulty: Medium
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks17(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks17(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs17 = callbacks17(['a', 'b']); console.assert(fs17[0]() === 'a');
```


## JS-M-018: prototype pollution

- Difficulty: Medium
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has18(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has18(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object18 = Object.create({hidden: true}); console.assert(has18(object18, 'hidden') === false);
```


## JS-M-019: missing await

- Difficulty: Medium
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load19() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load19() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load19() and assert the parsed value; reject a non-OK response.
```


## JS-M-020: unvalidated JSON

- Difficulty: Medium
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user20(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user20(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user20('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-M-021: loose equality

- Difficulty: Medium
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check21(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check21(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check21(0) === 'empty'); console.assert(check21('0') === 'filled');
```


## JS-M-022: truthiness and zero

- Difficulty: Medium
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label22(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label22(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label22(0) === 'present'); console.assert(label22(undefined) === 'missing');
```


## JS-M-023: array mutation

- Difficulty: Medium
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add23(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add23(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source23 = [1]; const result23 = add23(source23, 2); console.assert(source23.length === 1);
```


## JS-M-024: for in versus for of

- Difficulty: Medium
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum24(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum24(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum24([2, 3]) === 5);
```


## JS-M-025: default parameter

- Difficulty: Medium
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name25(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name25(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name25(null) === 'guest'); console.assert(name25(undefined) === 'guest');
```


## JS-M-026: reduce without identity

- Difficulty: Medium
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total26(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total26(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total26([]) === 0); console.assert(total26([2, 3]) === 5);
```


## JS-M-027: loop capture

- Difficulty: Medium
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks27(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks27(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs27 = callbacks27(['a', 'b']); console.assert(fs27[0]() === 'a');
```


## JS-M-028: prototype pollution

- Difficulty: Medium
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has28(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has28(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object28 = Object.create({hidden: true}); console.assert(has28(object28, 'hidden') === false);
```


## JS-M-029: missing await

- Difficulty: Medium
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load29() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load29() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load29() and assert the parsed value; reject a non-OK response.
```


## JS-M-030: unvalidated JSON

- Difficulty: Medium
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user30(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user30(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user30('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-M-031: loose equality

- Difficulty: Medium
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check31(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check31(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check31(0) === 'empty'); console.assert(check31('0') === 'filled');
```


## JS-M-032: truthiness and zero

- Difficulty: Medium
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label32(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label32(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label32(0) === 'present'); console.assert(label32(undefined) === 'missing');
```


## JS-M-033: array mutation

- Difficulty: Medium
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add33(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add33(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source33 = [1]; const result33 = add33(source33, 2); console.assert(source33.length === 1);
```


## JS-M-034: for in versus for of

- Difficulty: Medium
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum34(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum34(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum34([2, 3]) === 5);
```


## JS-M-035: default parameter

- Difficulty: Medium
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name35(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name35(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name35(null) === 'guest'); console.assert(name35(undefined) === 'guest');
```


## JS-M-036: reduce without identity

- Difficulty: Medium
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total36(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total36(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total36([]) === 0); console.assert(total36([2, 3]) === 5);
```


## JS-M-037: loop capture

- Difficulty: Medium
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks37(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks37(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs37 = callbacks37(['a', 'b']); console.assert(fs37[0]() === 'a');
```


## JS-M-038: prototype pollution

- Difficulty: Medium
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has38(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has38(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object38 = Object.create({hidden: true}); console.assert(has38(object38, 'hidden') === false);
```


## JS-M-039: missing await

- Difficulty: Medium
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load39() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load39() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load39() and assert the parsed value; reject a non-OK response.
```


## JS-M-040: unvalidated JSON

- Difficulty: Medium
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user40(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user40(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user40('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-M-041: loose equality

- Difficulty: Medium
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check41(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check41(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check41(0) === 'empty'); console.assert(check41('0') === 'filled');
```


## JS-M-042: truthiness and zero

- Difficulty: Medium
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label42(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label42(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label42(0) === 'present'); console.assert(label42(undefined) === 'missing');
```


## JS-M-043: array mutation

- Difficulty: Medium
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add43(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add43(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source43 = [1]; const result43 = add43(source43, 2); console.assert(source43.length === 1);
```


## JS-M-044: for in versus for of

- Difficulty: Medium
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum44(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum44(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum44([2, 3]) === 5);
```


## JS-M-045: default parameter

- Difficulty: Medium
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name45(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name45(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name45(null) === 'guest'); console.assert(name45(undefined) === 'guest');
```


## JS-M-046: reduce without identity

- Difficulty: Medium
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total46(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total46(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total46([]) === 0); console.assert(total46([2, 3]) === 5);
```


## JS-M-047: loop capture

- Difficulty: Medium
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks47(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks47(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs47 = callbacks47(['a', 'b']); console.assert(fs47[0]() === 'a');
```


## JS-M-048: prototype pollution

- Difficulty: Medium
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has48(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has48(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object48 = Object.create({hidden: true}); console.assert(has48(object48, 'hidden') === false);
```


## JS-M-049: missing await

- Difficulty: Medium
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load49() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load49() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load49() and assert the parsed value; reject a non-OK response.
```


## JS-M-050: unvalidated JSON

- Difficulty: Medium
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user50(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user50(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user50('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-M-051: loose equality

- Difficulty: Medium
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check51(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check51(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check51(0) === 'empty'); console.assert(check51('0') === 'filled');
```


## JS-M-052: truthiness and zero

- Difficulty: Medium
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label52(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label52(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label52(0) === 'present'); console.assert(label52(undefined) === 'missing');
```


## JS-M-053: array mutation

- Difficulty: Medium
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add53(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add53(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source53 = [1]; const result53 = add53(source53, 2); console.assert(source53.length === 1);
```


## JS-M-054: for in versus for of

- Difficulty: Medium
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum54(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum54(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum54([2, 3]) === 5);
```


## JS-M-055: default parameter

- Difficulty: Medium
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name55(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name55(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name55(null) === 'guest'); console.assert(name55(undefined) === 'guest');
```


## JS-M-056: reduce without identity

- Difficulty: Medium
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total56(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total56(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total56([]) === 0); console.assert(total56([2, 3]) === 5);
```


## JS-M-057: loop capture

- Difficulty: Medium
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks57(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks57(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs57 = callbacks57(['a', 'b']); console.assert(fs57[0]() === 'a');
```


## JS-M-058: prototype pollution

- Difficulty: Medium
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has58(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has58(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object58 = Object.create({hidden: true}); console.assert(has58(object58, 'hidden') === false);
```


## JS-M-059: missing await

- Difficulty: Medium
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load59() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load59() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load59() and assert the parsed value; reject a non-OK response.
```


## JS-M-060: unvalidated JSON

- Difficulty: Medium
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user60(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user60(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user60('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-M-061: loose equality

- Difficulty: Medium
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check61(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check61(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check61(0) === 'empty'); console.assert(check61('0') === 'filled');
```


## JS-M-062: truthiness and zero

- Difficulty: Medium
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label62(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label62(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label62(0) === 'present'); console.assert(label62(undefined) === 'missing');
```


## JS-M-063: array mutation

- Difficulty: Medium
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add63(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add63(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source63 = [1]; const result63 = add63(source63, 2); console.assert(source63.length === 1);
```


## JS-M-064: for in versus for of

- Difficulty: Medium
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum64(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum64(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum64([2, 3]) === 5);
```


## JS-M-065: default parameter

- Difficulty: Medium
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name65(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name65(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name65(null) === 'guest'); console.assert(name65(undefined) === 'guest');
```


## JS-M-066: reduce without identity

- Difficulty: Medium
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total66(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total66(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total66([]) === 0); console.assert(total66([2, 3]) === 5);
```


## JS-M-067: loop capture

- Difficulty: Medium
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks67(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks67(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs67 = callbacks67(['a', 'b']); console.assert(fs67[0]() === 'a');
```


## JS-M-068: prototype pollution

- Difficulty: Medium
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has68(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has68(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object68 = Object.create({hidden: true}); console.assert(has68(object68, 'hidden') === false);
```


## JS-M-069: missing await

- Difficulty: Medium
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load69() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load69() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load69() and assert the parsed value; reject a non-OK response.
```


## JS-M-070: unvalidated JSON

- Difficulty: Medium
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user70(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user70(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user70('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-M-071: loose equality

- Difficulty: Medium
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check71(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check71(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check71(0) === 'empty'); console.assert(check71('0') === 'filled');
```


## JS-M-072: truthiness and zero

- Difficulty: Medium
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label72(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label72(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label72(0) === 'present'); console.assert(label72(undefined) === 'missing');
```


## JS-M-073: array mutation

- Difficulty: Medium
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add73(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add73(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source73 = [1]; const result73 = add73(source73, 2); console.assert(source73.length === 1);
```


## JS-M-074: for in versus for of

- Difficulty: Medium
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum74(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum74(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum74([2, 3]) === 5);
```


## JS-M-075: default parameter

- Difficulty: Medium
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name75(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name75(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name75(null) === 'guest'); console.assert(name75(undefined) === 'guest');
```


## JS-M-076: reduce without identity

- Difficulty: Medium
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total76(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total76(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total76([]) === 0); console.assert(total76([2, 3]) === 5);
```


## JS-M-077: loop capture

- Difficulty: Medium
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks77(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks77(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs77 = callbacks77(['a', 'b']); console.assert(fs77[0]() === 'a');
```


## JS-M-078: prototype pollution

- Difficulty: Medium
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has78(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has78(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object78 = Object.create({hidden: true}); console.assert(has78(object78, 'hidden') === false);
```


## JS-M-079: missing await

- Difficulty: Medium
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load79() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load79() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load79() and assert the parsed value; reject a non-OK response.
```


## JS-M-080: unvalidated JSON

- Difficulty: Medium
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user80(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user80(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user80('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-M-081: loose equality

- Difficulty: Medium
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check81(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check81(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check81(0) === 'empty'); console.assert(check81('0') === 'filled');
```


## JS-M-082: truthiness and zero

- Difficulty: Medium
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label82(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label82(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label82(0) === 'present'); console.assert(label82(undefined) === 'missing');
```


## JS-M-083: array mutation

- Difficulty: Medium
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add83(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add83(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source83 = [1]; const result83 = add83(source83, 2); console.assert(source83.length === 1);
```


## JS-M-084: for in versus for of

- Difficulty: Medium
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum84(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum84(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum84([2, 3]) === 5);
```


## JS-M-085: default parameter

- Difficulty: Medium
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name85(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name85(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name85(null) === 'guest'); console.assert(name85(undefined) === 'guest');
```


## JS-M-086: reduce without identity

- Difficulty: Medium
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total86(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total86(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total86([]) === 0); console.assert(total86([2, 3]) === 5);
```


## JS-M-087: loop capture

- Difficulty: Medium
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks87(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks87(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs87 = callbacks87(['a', 'b']); console.assert(fs87[0]() === 'a');
```


## JS-M-088: prototype pollution

- Difficulty: Medium
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has88(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has88(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object88 = Object.create({hidden: true}); console.assert(has88(object88, 'hidden') === false);
```


## JS-M-089: missing await

- Difficulty: Medium
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load89() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load89() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load89() and assert the parsed value; reject a non-OK response.
```


## JS-M-090: unvalidated JSON

- Difficulty: Medium
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user90(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user90(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user90('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-M-091: loose equality

- Difficulty: Medium
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check91(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check91(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check91(0) === 'empty'); console.assert(check91('0') === 'filled');
```


## JS-M-092: truthiness and zero

- Difficulty: Medium
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label92(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label92(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label92(0) === 'present'); console.assert(label92(undefined) === 'missing');
```


## JS-M-093: array mutation

- Difficulty: Medium
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add93(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add93(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source93 = [1]; const result93 = add93(source93, 2); console.assert(source93.length === 1);
```


## JS-M-094: for in versus for of

- Difficulty: Medium
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum94(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum94(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum94([2, 3]) === 5);
```


## JS-M-095: default parameter

- Difficulty: Medium
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name95(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name95(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name95(null) === 'guest'); console.assert(name95(undefined) === 'guest');
```


## JS-M-096: reduce without identity

- Difficulty: Medium
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total96(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total96(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total96([]) === 0); console.assert(total96([2, 3]) === 5);
```


## JS-M-097: loop capture

- Difficulty: Medium
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks97(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks97(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs97 = callbacks97(['a', 'b']); console.assert(fs97[0]() === 'a');
```


## JS-M-098: prototype pollution

- Difficulty: Medium
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has98(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has98(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object98 = Object.create({hidden: true}); console.assert(has98(object98, 'hidden') === false);
```


## JS-M-099: missing await

- Difficulty: Medium
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load99() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load99() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load99() and assert the parsed value; reject a non-OK response.
```


## JS-M-100: unvalidated JSON

- Difficulty: Medium
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user100(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user100(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user100('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-H-001: loose equality

- Difficulty: Hard
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check1(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check1(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check1(0) === 'empty'); console.assert(check1('0') === 'filled');
```


## JS-H-002: truthiness and zero

- Difficulty: Hard
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label2(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label2(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label2(0) === 'present'); console.assert(label2(undefined) === 'missing');
```


## JS-H-003: array mutation

- Difficulty: Hard
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add3(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add3(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source3 = [1]; const result3 = add3(source3, 2); console.assert(source3.length === 1);
```


## JS-H-004: for in versus for of

- Difficulty: Hard
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum4(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum4(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum4([2, 3]) === 5);
```


## JS-H-005: default parameter

- Difficulty: Hard
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name5(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name5(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name5(null) === 'guest'); console.assert(name5(undefined) === 'guest');
```


## JS-H-006: reduce without identity

- Difficulty: Hard
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total6(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total6(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total6([]) === 0); console.assert(total6([2, 3]) === 5);
```


## JS-H-007: loop capture

- Difficulty: Hard
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks7(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks7(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs7 = callbacks7(['a', 'b']); console.assert(fs7[0]() === 'a');
```


## JS-H-008: prototype pollution

- Difficulty: Hard
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has8(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has8(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object8 = Object.create({hidden: true}); console.assert(has8(object8, 'hidden') === false);
```


## JS-H-009: missing await

- Difficulty: Hard
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load9() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load9() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load9() and assert the parsed value; reject a non-OK response.
```


## JS-H-010: unvalidated JSON

- Difficulty: Hard
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user10(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user10(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user10('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-H-011: loose equality

- Difficulty: Hard
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check11(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check11(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check11(0) === 'empty'); console.assert(check11('0') === 'filled');
```


## JS-H-012: truthiness and zero

- Difficulty: Hard
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label12(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label12(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label12(0) === 'present'); console.assert(label12(undefined) === 'missing');
```


## JS-H-013: array mutation

- Difficulty: Hard
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add13(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add13(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source13 = [1]; const result13 = add13(source13, 2); console.assert(source13.length === 1);
```


## JS-H-014: for in versus for of

- Difficulty: Hard
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum14(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum14(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum14([2, 3]) === 5);
```


## JS-H-015: default parameter

- Difficulty: Hard
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name15(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name15(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name15(null) === 'guest'); console.assert(name15(undefined) === 'guest');
```


## JS-H-016: reduce without identity

- Difficulty: Hard
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total16(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total16(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total16([]) === 0); console.assert(total16([2, 3]) === 5);
```


## JS-H-017: loop capture

- Difficulty: Hard
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks17(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks17(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs17 = callbacks17(['a', 'b']); console.assert(fs17[0]() === 'a');
```


## JS-H-018: prototype pollution

- Difficulty: Hard
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has18(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has18(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object18 = Object.create({hidden: true}); console.assert(has18(object18, 'hidden') === false);
```


## JS-H-019: missing await

- Difficulty: Hard
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load19() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load19() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load19() and assert the parsed value; reject a non-OK response.
```


## JS-H-020: unvalidated JSON

- Difficulty: Hard
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user20(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user20(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user20('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-H-021: loose equality

- Difficulty: Hard
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check21(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check21(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check21(0) === 'empty'); console.assert(check21('0') === 'filled');
```


## JS-H-022: truthiness and zero

- Difficulty: Hard
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label22(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label22(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label22(0) === 'present'); console.assert(label22(undefined) === 'missing');
```


## JS-H-023: array mutation

- Difficulty: Hard
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add23(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add23(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source23 = [1]; const result23 = add23(source23, 2); console.assert(source23.length === 1);
```


## JS-H-024: for in versus for of

- Difficulty: Hard
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum24(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum24(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum24([2, 3]) === 5);
```


## JS-H-025: default parameter

- Difficulty: Hard
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name25(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name25(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name25(null) === 'guest'); console.assert(name25(undefined) === 'guest');
```


## JS-H-026: reduce without identity

- Difficulty: Hard
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total26(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total26(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total26([]) === 0); console.assert(total26([2, 3]) === 5);
```


## JS-H-027: loop capture

- Difficulty: Hard
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks27(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks27(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs27 = callbacks27(['a', 'b']); console.assert(fs27[0]() === 'a');
```


## JS-H-028: prototype pollution

- Difficulty: Hard
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has28(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has28(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object28 = Object.create({hidden: true}); console.assert(has28(object28, 'hidden') === false);
```


## JS-H-029: missing await

- Difficulty: Hard
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load29() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load29() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load29() and assert the parsed value; reject a non-OK response.
```


## JS-H-030: unvalidated JSON

- Difficulty: Hard
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user30(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user30(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user30('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-H-031: loose equality

- Difficulty: Hard
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check31(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check31(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check31(0) === 'empty'); console.assert(check31('0') === 'filled');
```


## JS-H-032: truthiness and zero

- Difficulty: Hard
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label32(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label32(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label32(0) === 'present'); console.assert(label32(undefined) === 'missing');
```


## JS-H-033: array mutation

- Difficulty: Hard
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add33(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add33(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source33 = [1]; const result33 = add33(source33, 2); console.assert(source33.length === 1);
```


## JS-H-034: for in versus for of

- Difficulty: Hard
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum34(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum34(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum34([2, 3]) === 5);
```


## JS-H-035: default parameter

- Difficulty: Hard
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name35(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name35(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name35(null) === 'guest'); console.assert(name35(undefined) === 'guest');
```


## JS-H-036: reduce without identity

- Difficulty: Hard
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total36(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total36(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total36([]) === 0); console.assert(total36([2, 3]) === 5);
```


## JS-H-037: loop capture

- Difficulty: Hard
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks37(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks37(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs37 = callbacks37(['a', 'b']); console.assert(fs37[0]() === 'a');
```


## JS-H-038: prototype pollution

- Difficulty: Hard
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has38(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has38(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object38 = Object.create({hidden: true}); console.assert(has38(object38, 'hidden') === false);
```


## JS-H-039: missing await

- Difficulty: Hard
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load39() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load39() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load39() and assert the parsed value; reject a non-OK response.
```


## JS-H-040: unvalidated JSON

- Difficulty: Hard
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user40(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user40(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user40('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-H-041: loose equality

- Difficulty: Hard
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check41(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check41(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check41(0) === 'empty'); console.assert(check41('0') === 'filled');
```


## JS-H-042: truthiness and zero

- Difficulty: Hard
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label42(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label42(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label42(0) === 'present'); console.assert(label42(undefined) === 'missing');
```


## JS-H-043: array mutation

- Difficulty: Hard
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add43(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add43(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source43 = [1]; const result43 = add43(source43, 2); console.assert(source43.length === 1);
```


## JS-H-044: for in versus for of

- Difficulty: Hard
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum44(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum44(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum44([2, 3]) === 5);
```


## JS-H-045: default parameter

- Difficulty: Hard
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name45(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name45(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name45(null) === 'guest'); console.assert(name45(undefined) === 'guest');
```


## JS-H-046: reduce without identity

- Difficulty: Hard
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total46(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total46(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total46([]) === 0); console.assert(total46([2, 3]) === 5);
```


## JS-H-047: loop capture

- Difficulty: Hard
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks47(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks47(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs47 = callbacks47(['a', 'b']); console.assert(fs47[0]() === 'a');
```


## JS-H-048: prototype pollution

- Difficulty: Hard
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has48(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has48(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object48 = Object.create({hidden: true}); console.assert(has48(object48, 'hidden') === false);
```


## JS-H-049: missing await

- Difficulty: Hard
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load49() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load49() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load49() and assert the parsed value; reject a non-OK response.
```


## JS-H-050: unvalidated JSON

- Difficulty: Hard
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user50(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user50(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user50('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-H-051: loose equality

- Difficulty: Hard
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check51(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check51(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check51(0) === 'empty'); console.assert(check51('0') === 'filled');
```


## JS-H-052: truthiness and zero

- Difficulty: Hard
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label52(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label52(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label52(0) === 'present'); console.assert(label52(undefined) === 'missing');
```


## JS-H-053: array mutation

- Difficulty: Hard
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add53(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add53(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source53 = [1]; const result53 = add53(source53, 2); console.assert(source53.length === 1);
```


## JS-H-054: for in versus for of

- Difficulty: Hard
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum54(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum54(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum54([2, 3]) === 5);
```


## JS-H-055: default parameter

- Difficulty: Hard
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name55(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name55(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name55(null) === 'guest'); console.assert(name55(undefined) === 'guest');
```


## JS-H-056: reduce without identity

- Difficulty: Hard
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total56(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total56(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total56([]) === 0); console.assert(total56([2, 3]) === 5);
```


## JS-H-057: loop capture

- Difficulty: Hard
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks57(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks57(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs57 = callbacks57(['a', 'b']); console.assert(fs57[0]() === 'a');
```


## JS-H-058: prototype pollution

- Difficulty: Hard
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has58(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has58(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object58 = Object.create({hidden: true}); console.assert(has58(object58, 'hidden') === false);
```


## JS-H-059: missing await

- Difficulty: Hard
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load59() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load59() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load59() and assert the parsed value; reject a non-OK response.
```


## JS-H-060: unvalidated JSON

- Difficulty: Hard
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user60(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user60(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user60('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-H-061: loose equality

- Difficulty: Hard
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check61(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check61(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check61(0) === 'empty'); console.assert(check61('0') === 'filled');
```


## JS-H-062: truthiness and zero

- Difficulty: Hard
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label62(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label62(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label62(0) === 'present'); console.assert(label62(undefined) === 'missing');
```


## JS-H-063: array mutation

- Difficulty: Hard
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add63(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add63(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source63 = [1]; const result63 = add63(source63, 2); console.assert(source63.length === 1);
```


## JS-H-064: for in versus for of

- Difficulty: Hard
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum64(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum64(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum64([2, 3]) === 5);
```


## JS-H-065: default parameter

- Difficulty: Hard
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name65(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name65(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name65(null) === 'guest'); console.assert(name65(undefined) === 'guest');
```


## JS-H-066: reduce without identity

- Difficulty: Hard
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total66(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total66(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total66([]) === 0); console.assert(total66([2, 3]) === 5);
```


## JS-H-067: loop capture

- Difficulty: Hard
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks67(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks67(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs67 = callbacks67(['a', 'b']); console.assert(fs67[0]() === 'a');
```


## JS-H-068: prototype pollution

- Difficulty: Hard
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has68(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has68(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object68 = Object.create({hidden: true}); console.assert(has68(object68, 'hidden') === false);
```


## JS-H-069: missing await

- Difficulty: Hard
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load69() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load69() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load69() and assert the parsed value; reject a non-OK response.
```


## JS-H-070: unvalidated JSON

- Difficulty: Hard
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user70(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user70(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user70('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-H-071: loose equality

- Difficulty: Hard
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check71(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check71(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check71(0) === 'empty'); console.assert(check71('0') === 'filled');
```


## JS-H-072: truthiness and zero

- Difficulty: Hard
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label72(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label72(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label72(0) === 'present'); console.assert(label72(undefined) === 'missing');
```


## JS-H-073: array mutation

- Difficulty: Hard
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add73(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add73(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source73 = [1]; const result73 = add73(source73, 2); console.assert(source73.length === 1);
```


## JS-H-074: for in versus for of

- Difficulty: Hard
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum74(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum74(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum74([2, 3]) === 5);
```


## JS-H-075: default parameter

- Difficulty: Hard
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name75(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name75(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name75(null) === 'guest'); console.assert(name75(undefined) === 'guest');
```


## JS-H-076: reduce without identity

- Difficulty: Hard
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total76(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total76(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total76([]) === 0); console.assert(total76([2, 3]) === 5);
```


## JS-H-077: loop capture

- Difficulty: Hard
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks77(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks77(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs77 = callbacks77(['a', 'b']); console.assert(fs77[0]() === 'a');
```


## JS-H-078: prototype pollution

- Difficulty: Hard
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has78(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has78(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object78 = Object.create({hidden: true}); console.assert(has78(object78, 'hidden') === false);
```


## JS-H-079: missing await

- Difficulty: Hard
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load79() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load79() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load79() and assert the parsed value; reject a non-OK response.
```


## JS-H-080: unvalidated JSON

- Difficulty: Hard
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user80(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user80(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user80('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-H-081: loose equality

- Difficulty: Hard
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check81(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check81(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check81(0) === 'empty'); console.assert(check81('0') === 'filled');
```


## JS-H-082: truthiness and zero

- Difficulty: Hard
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label82(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label82(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label82(0) === 'present'); console.assert(label82(undefined) === 'missing');
```


## JS-H-083: array mutation

- Difficulty: Hard
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add83(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add83(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source83 = [1]; const result83 = add83(source83, 2); console.assert(source83.length === 1);
```


## JS-H-084: for in versus for of

- Difficulty: Hard
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum84(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum84(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum84([2, 3]) === 5);
```


## JS-H-085: default parameter

- Difficulty: Hard
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name85(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name85(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name85(null) === 'guest'); console.assert(name85(undefined) === 'guest');
```


## JS-H-086: reduce without identity

- Difficulty: Hard
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total86(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total86(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total86([]) === 0); console.assert(total86([2, 3]) === 5);
```


## JS-H-087: loop capture

- Difficulty: Hard
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks87(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks87(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs87 = callbacks87(['a', 'b']); console.assert(fs87[0]() === 'a');
```


## JS-H-088: prototype pollution

- Difficulty: Hard
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has88(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has88(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object88 = Object.create({hidden: true}); console.assert(has88(object88, 'hidden') === false);
```


## JS-H-089: missing await

- Difficulty: Hard
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load89() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load89() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load89() and assert the parsed value; reject a non-OK response.
```


## JS-H-090: unvalidated JSON

- Difficulty: Hard
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user90(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user90(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user90('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```


## JS-H-091: loose equality

- Difficulty: Hard
- Language: JavaScript
- Perspective: Output tracing
- Concept: loose equality
- Symptom: The branch accepts an unexpected value.
- Diagnostic goal: Trace coercion before comparing values.

### Buggy code

```javascript
function check91(value) { return value == 0 ? 'empty' : 'filled'; }
```

### Expected diagnosis

Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.

### Corrected code

```javascript
function check91(value) { return value === 0 ? 'empty' : 'filled'; }
```

### Regression tests

```javascript
console.assert(check91(0) === 'empty'); console.assert(check91('0') === 'filled');
```


## JS-H-092: truthiness and zero

- Difficulty: Hard
- Language: JavaScript
- Perspective: Boundary analysis
- Concept: truthiness and zero
- Symptom: A valid zero is treated as absent.
- Diagnostic goal: Separate falsy values from missing values.

### Buggy code

```javascript
function label92(count) { return count ? 'present' : 'missing'; }
```

### Expected diagnosis

JavaScript treats 0 as falsy even when it is a valid domain value.

### Corrected code

```javascript
function label92(count) { return count === undefined ? 'missing' : 'present'; }
```

### Regression tests

```javascript
console.assert(label92(0) === 'present'); console.assert(label92(undefined) === 'missing');
```


## JS-H-093: array mutation

- Difficulty: Hard
- Language: JavaScript
- Perspective: State tracing
- Concept: array mutation
- Symptom: The caller's array changes unexpectedly.
- Diagnostic goal: Identify the shared reference.

### Buggy code

```javascript
function add93(items, value) { const copy = items; copy.push(value); return copy; }
```

### Expected diagnosis

Assigning an array copies its reference, so push mutates the caller's array.

### Corrected code

```javascript
function add93(items, value) { return [...items, value]; }
```

### Regression tests

```javascript
const source93 = [1]; const result93 = add93(source93, 2); console.assert(source93.length === 1);
```


## JS-H-094: for in versus for of

- Difficulty: Hard
- Language: JavaScript
- Perspective: Iteration reasoning
- Concept: for in versus for of
- Symptom: The result contains indexes instead of values.
- Diagnostic goal: Identify what the chosen iterator produces.

### Buggy code

```javascript
function sum94(items) { let total = 0; for (const item in items) total += item; return total; }
```

### Expected diagnosis

for...in yields property names, which are strings for array indexes; for...of yields elements.

### Corrected code

```javascript
function sum94(items) { let total = 0; for (const item of items) total += item; return total; }
```

### Regression tests

```javascript
console.assert(sum94([2, 3]) === 5);
```


## JS-H-095: default parameter

- Difficulty: Hard
- Language: JavaScript
- Perspective: Function contract
- Concept: default parameter
- Symptom: An explicit null does not receive the fallback.
- Diagnostic goal: Distinguish undefined defaults from null handling.

### Buggy code

```javascript
function name95(value = 'guest') { return value; }
```

### Expected diagnosis

Default parameters apply only when the argument is undefined, not when it is null.

### Corrected code

```javascript
function name95(value) { return value ?? 'guest'; }
```

### Regression tests

```javascript
console.assert(name95(null) === 'guest'); console.assert(name95(undefined) === 'guest');
```


## JS-H-096: reduce without identity

- Difficulty: Hard
- Language: JavaScript
- Perspective: Collection invariant
- Concept: reduce without identity
- Symptom: An empty input throws a TypeError.
- Diagnostic goal: Check the empty collection contract.

### Buggy code

```javascript
function total96(items) { return items.reduce((a, b) => a + b); }
```

### Expected diagnosis

reduce uses the first element when no initial value is supplied; an empty array has no first element.

### Corrected code

```javascript
function total96(items) { return items.reduce((a, b) => a + b, 0); }
```

### Regression tests

```javascript
console.assert(total96([]) === 0); console.assert(total96([2, 3]) === 5);
```


## JS-H-097: loop capture

- Difficulty: Hard
- Language: JavaScript
- Perspective: Closure reasoning
- Concept: loop capture
- Symptom: Every callback reports the final index.
- Diagnostic goal: Trace when the closure reads the loop variable.

### Buggy code

```javascript
function callbacks97(values) { var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Expected diagnosis

var is function-scoped, so every callback reads the final i after the loop ends.

### Corrected code

```javascript
function callbacks97(values) { const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }
```

### Regression tests

```javascript
const fs97 = callbacks97(['a', 'b']); console.assert(fs97[0]() === 'a');
```


## JS-H-098: prototype pollution

- Difficulty: Hard
- Language: JavaScript
- Perspective: Object semantics
- Concept: prototype pollution
- Symptom: A membership check sees an inherited property.
- Diagnostic goal: Distinguish own properties from inherited properties.

### Buggy code

```javascript
function has98(object, key) { return key in object; }
```

### Expected diagnosis

in searches the prototype chain, so inherited names can be mistaken for stored data.

### Corrected code

```javascript
function has98(object, key) { return Object.hasOwn(object, key); }
```

### Regression tests

```javascript
const object98 = Object.create({hidden: true}); console.assert(has98(object98, 'hidden') === false);
```


## JS-H-099: missing await

- Difficulty: Hard
- Language: JavaScript
- Perspective: Async ordering
- Concept: missing await
- Symptom: The function returns a Promise instead of the resolved value.
- Diagnostic goal: Trace the promise boundary.

### Buggy code

```javascript
async function load99() { return fetch('/data').json(); }
```

### Expected diagnosis

fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.

### Corrected code

```javascript
async function load99() { const response = await fetch('/data'); return await response.json(); }
```

### Regression tests

```javascript
// Regression: await load99() and assert the parsed value; reject a non-OK response.
```


## JS-H-100: unvalidated JSON

- Difficulty: Hard
- Language: JavaScript
- Perspective: Module/runtime boundary
- Concept: unvalidated JSON
- Symptom: A property access fails on malformed input.
- Diagnostic goal: Validate parsed data before trusting its shape.

### Buggy code

```javascript
function user100(text) { const value = JSON.parse(text); return value.name.toUpperCase(); }
```

### Expected diagnosis

JSON.parse checks syntax only; it does not prove that the result is an object with a string name.

### Corrected code

```javascript
function user100(text) { const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }
```

### Regression tests

```javascript
console.assert(user100('{"name":"Ada"}') === 'ADA'); // Regression: reject '{}'.
```
