# TypeScript Debug Exercises

A RAG-training corpus of 300 TypeScript debugging exercises. Corrected code is editorial material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: runtime behavior, type reasoning, state, contracts, collections, async control flow, security boundaries, and complexity


## TS-E-001: truthiness narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count1(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count1(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count1(0) === 'present'); console.assert(count1(undefined) === 'missing');
```


## TS-E-002: assertion is not validation

- Difficulty: Easy
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User2 = { name: string };
function parse2(text: string): User2 { return JSON.parse(text) as User2; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User2 = { name: string };
function parse2(text: string): User2 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User2; }
```

### Regression tests

```typescript
console.assert(parse2('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-E-003: unsafe generic assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first3<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first3<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first3([1, 2]) === 1); console.assert(first3([]) === undefined);
```


## TS-E-004: missing required field

- Difficulty: Easy
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config4 = { retries: number; timeout: number };
const config4 = { retries: 3 } as Config4;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config4 = { retries: number; timeout: number };
function makeConfig4(input: Partial<Config4>): Config4 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config4 = makeConfig4({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config4.timeout === 1000);
```


## TS-E-005: property access before narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result5 = { ok: true; value: number } | { ok: false; error: string };
function message5(result: Result5): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result5 = { ok: true; value: number } | { ok: false; error: string };
function message5(result: Result5): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message5({ok: true, value: 0}) === '0');
```


## TS-E-006: implicit any

- Difficulty: Easy
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values6 = [1, 2, 3];
const doubled6 = values6.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values6: number[] = [1, 2, 3];
const doubled6: number[] = values6.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled6[2] === 6); // Regression: compile with strict enabled.
```


## TS-E-007: non-null assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get7(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get7(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get7(['a'], 2) === undefined);
```


## TS-E-008: forgotten Promise

- Difficulty: Easy
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay8(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay8(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay8(10).then(value => console.assert(value === 10));
```


## TS-E-009: unchecked indexed access

- Difficulty: Easy
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last9(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last9(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last9([4, 5]) === 5); console.assert(last9([]) === undefined);
```


## TS-E-010: enum or string mismatch

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode10 = 'fast' | 'safe';
function run10(mode: Mode10) { return mode.toUpperCase(); }
const input10 = 'debug' as Mode10;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode10 = 'fast' | 'safe';
function parseMode10(input: string): Mode10 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input10 = parseMode10('safe');
```

### Regression tests

```typescript
console.assert(input10 === 'safe'); // Regression: parseMode10('debug') throws.
```


## TS-E-011: truthiness narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count11(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count11(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count11(0) === 'present'); console.assert(count11(undefined) === 'missing');
```


## TS-E-012: assertion is not validation

- Difficulty: Easy
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User12 = { name: string };
function parse12(text: string): User12 { return JSON.parse(text) as User12; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User12 = { name: string };
function parse12(text: string): User12 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User12; }
```

### Regression tests

```typescript
console.assert(parse12('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-E-013: unsafe generic assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first13<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first13<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first13([1, 2]) === 1); console.assert(first13([]) === undefined);
```


## TS-E-014: missing required field

- Difficulty: Easy
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config14 = { retries: number; timeout: number };
const config14 = { retries: 3 } as Config14;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config14 = { retries: number; timeout: number };
function makeConfig14(input: Partial<Config14>): Config14 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config14 = makeConfig14({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config14.timeout === 1000);
```


## TS-E-015: property access before narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result15 = { ok: true; value: number } | { ok: false; error: string };
function message15(result: Result15): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result15 = { ok: true; value: number } | { ok: false; error: string };
function message15(result: Result15): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message15({ok: true, value: 0}) === '0');
```


## TS-E-016: implicit any

- Difficulty: Easy
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values16 = [1, 2, 3];
const doubled16 = values16.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values16: number[] = [1, 2, 3];
const doubled16: number[] = values16.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled16[2] === 6); // Regression: compile with strict enabled.
```


## TS-E-017: non-null assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get17(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get17(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get17(['a'], 2) === undefined);
```


## TS-E-018: forgotten Promise

- Difficulty: Easy
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay18(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay18(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay18(10).then(value => console.assert(value === 10));
```


## TS-E-019: unchecked indexed access

- Difficulty: Easy
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last19(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last19(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last19([4, 5]) === 5); console.assert(last19([]) === undefined);
```


## TS-E-020: enum or string mismatch

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode20 = 'fast' | 'safe';
function run20(mode: Mode20) { return mode.toUpperCase(); }
const input20 = 'debug' as Mode20;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode20 = 'fast' | 'safe';
function parseMode20(input: string): Mode20 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input20 = parseMode20('safe');
```

### Regression tests

```typescript
console.assert(input20 === 'safe'); // Regression: parseMode20('debug') throws.
```


## TS-E-021: truthiness narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count21(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count21(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count21(0) === 'present'); console.assert(count21(undefined) === 'missing');
```


## TS-E-022: assertion is not validation

- Difficulty: Easy
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User22 = { name: string };
function parse22(text: string): User22 { return JSON.parse(text) as User22; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User22 = { name: string };
function parse22(text: string): User22 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User22; }
```

### Regression tests

```typescript
console.assert(parse22('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-E-023: unsafe generic assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first23<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first23<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first23([1, 2]) === 1); console.assert(first23([]) === undefined);
```


## TS-E-024: missing required field

- Difficulty: Easy
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config24 = { retries: number; timeout: number };
const config24 = { retries: 3 } as Config24;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config24 = { retries: number; timeout: number };
function makeConfig24(input: Partial<Config24>): Config24 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config24 = makeConfig24({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config24.timeout === 1000);
```


## TS-E-025: property access before narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result25 = { ok: true; value: number } | { ok: false; error: string };
function message25(result: Result25): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result25 = { ok: true; value: number } | { ok: false; error: string };
function message25(result: Result25): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message25({ok: true, value: 0}) === '0');
```


## TS-E-026: implicit any

- Difficulty: Easy
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values26 = [1, 2, 3];
const doubled26 = values26.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values26: number[] = [1, 2, 3];
const doubled26: number[] = values26.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled26[2] === 6); // Regression: compile with strict enabled.
```


## TS-E-027: non-null assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get27(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get27(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get27(['a'], 2) === undefined);
```


## TS-E-028: forgotten Promise

- Difficulty: Easy
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay28(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay28(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay28(10).then(value => console.assert(value === 10));
```


## TS-E-029: unchecked indexed access

- Difficulty: Easy
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last29(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last29(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last29([4, 5]) === 5); console.assert(last29([]) === undefined);
```


## TS-E-030: enum or string mismatch

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode30 = 'fast' | 'safe';
function run30(mode: Mode30) { return mode.toUpperCase(); }
const input30 = 'debug' as Mode30;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode30 = 'fast' | 'safe';
function parseMode30(input: string): Mode30 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input30 = parseMode30('safe');
```

### Regression tests

```typescript
console.assert(input30 === 'safe'); // Regression: parseMode30('debug') throws.
```


## TS-E-031: truthiness narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count31(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count31(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count31(0) === 'present'); console.assert(count31(undefined) === 'missing');
```


## TS-E-032: assertion is not validation

- Difficulty: Easy
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User32 = { name: string };
function parse32(text: string): User32 { return JSON.parse(text) as User32; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User32 = { name: string };
function parse32(text: string): User32 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User32; }
```

### Regression tests

```typescript
console.assert(parse32('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-E-033: unsafe generic assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first33<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first33<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first33([1, 2]) === 1); console.assert(first33([]) === undefined);
```


## TS-E-034: missing required field

- Difficulty: Easy
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config34 = { retries: number; timeout: number };
const config34 = { retries: 3 } as Config34;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config34 = { retries: number; timeout: number };
function makeConfig34(input: Partial<Config34>): Config34 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config34 = makeConfig34({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config34.timeout === 1000);
```


## TS-E-035: property access before narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result35 = { ok: true; value: number } | { ok: false; error: string };
function message35(result: Result35): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result35 = { ok: true; value: number } | { ok: false; error: string };
function message35(result: Result35): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message35({ok: true, value: 0}) === '0');
```


## TS-E-036: implicit any

- Difficulty: Easy
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values36 = [1, 2, 3];
const doubled36 = values36.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values36: number[] = [1, 2, 3];
const doubled36: number[] = values36.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled36[2] === 6); // Regression: compile with strict enabled.
```


## TS-E-037: non-null assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get37(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get37(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get37(['a'], 2) === undefined);
```


## TS-E-038: forgotten Promise

- Difficulty: Easy
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay38(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay38(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay38(10).then(value => console.assert(value === 10));
```


## TS-E-039: unchecked indexed access

- Difficulty: Easy
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last39(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last39(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last39([4, 5]) === 5); console.assert(last39([]) === undefined);
```


## TS-E-040: enum or string mismatch

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode40 = 'fast' | 'safe';
function run40(mode: Mode40) { return mode.toUpperCase(); }
const input40 = 'debug' as Mode40;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode40 = 'fast' | 'safe';
function parseMode40(input: string): Mode40 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input40 = parseMode40('safe');
```

### Regression tests

```typescript
console.assert(input40 === 'safe'); // Regression: parseMode40('debug') throws.
```


## TS-E-041: truthiness narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count41(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count41(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count41(0) === 'present'); console.assert(count41(undefined) === 'missing');
```


## TS-E-042: assertion is not validation

- Difficulty: Easy
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User42 = { name: string };
function parse42(text: string): User42 { return JSON.parse(text) as User42; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User42 = { name: string };
function parse42(text: string): User42 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User42; }
```

### Regression tests

```typescript
console.assert(parse42('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-E-043: unsafe generic assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first43<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first43<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first43([1, 2]) === 1); console.assert(first43([]) === undefined);
```


## TS-E-044: missing required field

- Difficulty: Easy
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config44 = { retries: number; timeout: number };
const config44 = { retries: 3 } as Config44;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config44 = { retries: number; timeout: number };
function makeConfig44(input: Partial<Config44>): Config44 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config44 = makeConfig44({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config44.timeout === 1000);
```


## TS-E-045: property access before narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result45 = { ok: true; value: number } | { ok: false; error: string };
function message45(result: Result45): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result45 = { ok: true; value: number } | { ok: false; error: string };
function message45(result: Result45): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message45({ok: true, value: 0}) === '0');
```


## TS-E-046: implicit any

- Difficulty: Easy
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values46 = [1, 2, 3];
const doubled46 = values46.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values46: number[] = [1, 2, 3];
const doubled46: number[] = values46.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled46[2] === 6); // Regression: compile with strict enabled.
```


## TS-E-047: non-null assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get47(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get47(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get47(['a'], 2) === undefined);
```


## TS-E-048: forgotten Promise

- Difficulty: Easy
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay48(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay48(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay48(10).then(value => console.assert(value === 10));
```


## TS-E-049: unchecked indexed access

- Difficulty: Easy
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last49(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last49(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last49([4, 5]) === 5); console.assert(last49([]) === undefined);
```


## TS-E-050: enum or string mismatch

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode50 = 'fast' | 'safe';
function run50(mode: Mode50) { return mode.toUpperCase(); }
const input50 = 'debug' as Mode50;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode50 = 'fast' | 'safe';
function parseMode50(input: string): Mode50 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input50 = parseMode50('safe');
```

### Regression tests

```typescript
console.assert(input50 === 'safe'); // Regression: parseMode50('debug') throws.
```


## TS-E-051: truthiness narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count51(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count51(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count51(0) === 'present'); console.assert(count51(undefined) === 'missing');
```


## TS-E-052: assertion is not validation

- Difficulty: Easy
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User52 = { name: string };
function parse52(text: string): User52 { return JSON.parse(text) as User52; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User52 = { name: string };
function parse52(text: string): User52 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User52; }
```

### Regression tests

```typescript
console.assert(parse52('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-E-053: unsafe generic assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first53<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first53<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first53([1, 2]) === 1); console.assert(first53([]) === undefined);
```


## TS-E-054: missing required field

- Difficulty: Easy
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config54 = { retries: number; timeout: number };
const config54 = { retries: 3 } as Config54;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config54 = { retries: number; timeout: number };
function makeConfig54(input: Partial<Config54>): Config54 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config54 = makeConfig54({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config54.timeout === 1000);
```


## TS-E-055: property access before narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result55 = { ok: true; value: number } | { ok: false; error: string };
function message55(result: Result55): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result55 = { ok: true; value: number } | { ok: false; error: string };
function message55(result: Result55): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message55({ok: true, value: 0}) === '0');
```


## TS-E-056: implicit any

- Difficulty: Easy
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values56 = [1, 2, 3];
const doubled56 = values56.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values56: number[] = [1, 2, 3];
const doubled56: number[] = values56.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled56[2] === 6); // Regression: compile with strict enabled.
```


## TS-E-057: non-null assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get57(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get57(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get57(['a'], 2) === undefined);
```


## TS-E-058: forgotten Promise

- Difficulty: Easy
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay58(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay58(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay58(10).then(value => console.assert(value === 10));
```


## TS-E-059: unchecked indexed access

- Difficulty: Easy
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last59(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last59(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last59([4, 5]) === 5); console.assert(last59([]) === undefined);
```


## TS-E-060: enum or string mismatch

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode60 = 'fast' | 'safe';
function run60(mode: Mode60) { return mode.toUpperCase(); }
const input60 = 'debug' as Mode60;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode60 = 'fast' | 'safe';
function parseMode60(input: string): Mode60 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input60 = parseMode60('safe');
```

### Regression tests

```typescript
console.assert(input60 === 'safe'); // Regression: parseMode60('debug') throws.
```


## TS-E-061: truthiness narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count61(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count61(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count61(0) === 'present'); console.assert(count61(undefined) === 'missing');
```


## TS-E-062: assertion is not validation

- Difficulty: Easy
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User62 = { name: string };
function parse62(text: string): User62 { return JSON.parse(text) as User62; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User62 = { name: string };
function parse62(text: string): User62 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User62; }
```

### Regression tests

```typescript
console.assert(parse62('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-E-063: unsafe generic assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first63<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first63<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first63([1, 2]) === 1); console.assert(first63([]) === undefined);
```


## TS-E-064: missing required field

- Difficulty: Easy
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config64 = { retries: number; timeout: number };
const config64 = { retries: 3 } as Config64;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config64 = { retries: number; timeout: number };
function makeConfig64(input: Partial<Config64>): Config64 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config64 = makeConfig64({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config64.timeout === 1000);
```


## TS-E-065: property access before narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result65 = { ok: true; value: number } | { ok: false; error: string };
function message65(result: Result65): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result65 = { ok: true; value: number } | { ok: false; error: string };
function message65(result: Result65): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message65({ok: true, value: 0}) === '0');
```


## TS-E-066: implicit any

- Difficulty: Easy
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values66 = [1, 2, 3];
const doubled66 = values66.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values66: number[] = [1, 2, 3];
const doubled66: number[] = values66.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled66[2] === 6); // Regression: compile with strict enabled.
```


## TS-E-067: non-null assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get67(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get67(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get67(['a'], 2) === undefined);
```


## TS-E-068: forgotten Promise

- Difficulty: Easy
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay68(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay68(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay68(10).then(value => console.assert(value === 10));
```


## TS-E-069: unchecked indexed access

- Difficulty: Easy
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last69(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last69(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last69([4, 5]) === 5); console.assert(last69([]) === undefined);
```


## TS-E-070: enum or string mismatch

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode70 = 'fast' | 'safe';
function run70(mode: Mode70) { return mode.toUpperCase(); }
const input70 = 'debug' as Mode70;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode70 = 'fast' | 'safe';
function parseMode70(input: string): Mode70 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input70 = parseMode70('safe');
```

### Regression tests

```typescript
console.assert(input70 === 'safe'); // Regression: parseMode70('debug') throws.
```


## TS-E-071: truthiness narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count71(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count71(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count71(0) === 'present'); console.assert(count71(undefined) === 'missing');
```


## TS-E-072: assertion is not validation

- Difficulty: Easy
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User72 = { name: string };
function parse72(text: string): User72 { return JSON.parse(text) as User72; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User72 = { name: string };
function parse72(text: string): User72 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User72; }
```

### Regression tests

```typescript
console.assert(parse72('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-E-073: unsafe generic assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first73<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first73<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first73([1, 2]) === 1); console.assert(first73([]) === undefined);
```


## TS-E-074: missing required field

- Difficulty: Easy
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config74 = { retries: number; timeout: number };
const config74 = { retries: 3 } as Config74;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config74 = { retries: number; timeout: number };
function makeConfig74(input: Partial<Config74>): Config74 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config74 = makeConfig74({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config74.timeout === 1000);
```


## TS-E-075: property access before narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result75 = { ok: true; value: number } | { ok: false; error: string };
function message75(result: Result75): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result75 = { ok: true; value: number } | { ok: false; error: string };
function message75(result: Result75): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message75({ok: true, value: 0}) === '0');
```


## TS-E-076: implicit any

- Difficulty: Easy
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values76 = [1, 2, 3];
const doubled76 = values76.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values76: number[] = [1, 2, 3];
const doubled76: number[] = values76.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled76[2] === 6); // Regression: compile with strict enabled.
```


## TS-E-077: non-null assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get77(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get77(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get77(['a'], 2) === undefined);
```


## TS-E-078: forgotten Promise

- Difficulty: Easy
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay78(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay78(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay78(10).then(value => console.assert(value === 10));
```


## TS-E-079: unchecked indexed access

- Difficulty: Easy
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last79(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last79(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last79([4, 5]) === 5); console.assert(last79([]) === undefined);
```


## TS-E-080: enum or string mismatch

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode80 = 'fast' | 'safe';
function run80(mode: Mode80) { return mode.toUpperCase(); }
const input80 = 'debug' as Mode80;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode80 = 'fast' | 'safe';
function parseMode80(input: string): Mode80 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input80 = parseMode80('safe');
```

### Regression tests

```typescript
console.assert(input80 === 'safe'); // Regression: parseMode80('debug') throws.
```


## TS-E-081: truthiness narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count81(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count81(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count81(0) === 'present'); console.assert(count81(undefined) === 'missing');
```


## TS-E-082: assertion is not validation

- Difficulty: Easy
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User82 = { name: string };
function parse82(text: string): User82 { return JSON.parse(text) as User82; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User82 = { name: string };
function parse82(text: string): User82 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User82; }
```

### Regression tests

```typescript
console.assert(parse82('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-E-083: unsafe generic assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first83<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first83<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first83([1, 2]) === 1); console.assert(first83([]) === undefined);
```


## TS-E-084: missing required field

- Difficulty: Easy
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config84 = { retries: number; timeout: number };
const config84 = { retries: 3 } as Config84;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config84 = { retries: number; timeout: number };
function makeConfig84(input: Partial<Config84>): Config84 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config84 = makeConfig84({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config84.timeout === 1000);
```


## TS-E-085: property access before narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result85 = { ok: true; value: number } | { ok: false; error: string };
function message85(result: Result85): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result85 = { ok: true; value: number } | { ok: false; error: string };
function message85(result: Result85): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message85({ok: true, value: 0}) === '0');
```


## TS-E-086: implicit any

- Difficulty: Easy
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values86 = [1, 2, 3];
const doubled86 = values86.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values86: number[] = [1, 2, 3];
const doubled86: number[] = values86.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled86[2] === 6); // Regression: compile with strict enabled.
```


## TS-E-087: non-null assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get87(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get87(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get87(['a'], 2) === undefined);
```


## TS-E-088: forgotten Promise

- Difficulty: Easy
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay88(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay88(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay88(10).then(value => console.assert(value === 10));
```


## TS-E-089: unchecked indexed access

- Difficulty: Easy
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last89(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last89(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last89([4, 5]) === 5); console.assert(last89([]) === undefined);
```


## TS-E-090: enum or string mismatch

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode90 = 'fast' | 'safe';
function run90(mode: Mode90) { return mode.toUpperCase(); }
const input90 = 'debug' as Mode90;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode90 = 'fast' | 'safe';
function parseMode90(input: string): Mode90 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input90 = parseMode90('safe');
```

### Regression tests

```typescript
console.assert(input90 === 'safe'); // Regression: parseMode90('debug') throws.
```


## TS-E-091: truthiness narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count91(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count91(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count91(0) === 'present'); console.assert(count91(undefined) === 'missing');
```


## TS-E-092: assertion is not validation

- Difficulty: Easy
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User92 = { name: string };
function parse92(text: string): User92 { return JSON.parse(text) as User92; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User92 = { name: string };
function parse92(text: string): User92 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User92; }
```

### Regression tests

```typescript
console.assert(parse92('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-E-093: unsafe generic assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first93<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first93<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first93([1, 2]) === 1); console.assert(first93([]) === undefined);
```


## TS-E-094: missing required field

- Difficulty: Easy
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config94 = { retries: number; timeout: number };
const config94 = { retries: 3 } as Config94;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config94 = { retries: number; timeout: number };
function makeConfig94(input: Partial<Config94>): Config94 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config94 = makeConfig94({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config94.timeout === 1000);
```


## TS-E-095: property access before narrowing

- Difficulty: Easy
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result95 = { ok: true; value: number } | { ok: false; error: string };
function message95(result: Result95): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result95 = { ok: true; value: number } | { ok: false; error: string };
function message95(result: Result95): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message95({ok: true, value: 0}) === '0');
```


## TS-E-096: implicit any

- Difficulty: Easy
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values96 = [1, 2, 3];
const doubled96 = values96.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values96: number[] = [1, 2, 3];
const doubled96: number[] = values96.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled96[2] === 6); // Regression: compile with strict enabled.
```


## TS-E-097: non-null assertion

- Difficulty: Easy
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get97(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get97(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get97(['a'], 2) === undefined);
```


## TS-E-098: forgotten Promise

- Difficulty: Easy
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay98(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay98(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay98(10).then(value => console.assert(value === 10));
```


## TS-E-099: unchecked indexed access

- Difficulty: Easy
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last99(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last99(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last99([4, 5]) === 5); console.assert(last99([]) === undefined);
```


## TS-E-100: enum or string mismatch

- Difficulty: Easy
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode100 = 'fast' | 'safe';
function run100(mode: Mode100) { return mode.toUpperCase(); }
const input100 = 'debug' as Mode100;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode100 = 'fast' | 'safe';
function parseMode100(input: string): Mode100 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input100 = parseMode100('safe');
```

### Regression tests

```typescript
console.assert(input100 === 'safe'); // Regression: parseMode100('debug') throws.
```


## TS-M-001: truthiness narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count1(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count1(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count1(0) === 'present'); console.assert(count1(undefined) === 'missing');
```


## TS-M-002: assertion is not validation

- Difficulty: Medium
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User2 = { name: string };
function parse2(text: string): User2 { return JSON.parse(text) as User2; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User2 = { name: string };
function parse2(text: string): User2 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User2; }
```

### Regression tests

```typescript
console.assert(parse2('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-M-003: unsafe generic assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first3<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first3<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first3([1, 2]) === 1); console.assert(first3([]) === undefined);
```


## TS-M-004: missing required field

- Difficulty: Medium
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config4 = { retries: number; timeout: number };
const config4 = { retries: 3 } as Config4;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config4 = { retries: number; timeout: number };
function makeConfig4(input: Partial<Config4>): Config4 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config4 = makeConfig4({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config4.timeout === 1000);
```


## TS-M-005: property access before narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result5 = { ok: true; value: number } | { ok: false; error: string };
function message5(result: Result5): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result5 = { ok: true; value: number } | { ok: false; error: string };
function message5(result: Result5): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message5({ok: true, value: 0}) === '0');
```


## TS-M-006: implicit any

- Difficulty: Medium
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values6 = [1, 2, 3];
const doubled6 = values6.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values6: number[] = [1, 2, 3];
const doubled6: number[] = values6.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled6[2] === 6); // Regression: compile with strict enabled.
```


## TS-M-007: non-null assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get7(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get7(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get7(['a'], 2) === undefined);
```


## TS-M-008: forgotten Promise

- Difficulty: Medium
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay8(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay8(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay8(10).then(value => console.assert(value === 10));
```


## TS-M-009: unchecked indexed access

- Difficulty: Medium
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last9(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last9(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last9([4, 5]) === 5); console.assert(last9([]) === undefined);
```


## TS-M-010: enum or string mismatch

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode10 = 'fast' | 'safe';
function run10(mode: Mode10) { return mode.toUpperCase(); }
const input10 = 'debug' as Mode10;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode10 = 'fast' | 'safe';
function parseMode10(input: string): Mode10 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input10 = parseMode10('safe');
```

### Regression tests

```typescript
console.assert(input10 === 'safe'); // Regression: parseMode10('debug') throws.
```


## TS-M-011: truthiness narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count11(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count11(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count11(0) === 'present'); console.assert(count11(undefined) === 'missing');
```


## TS-M-012: assertion is not validation

- Difficulty: Medium
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User12 = { name: string };
function parse12(text: string): User12 { return JSON.parse(text) as User12; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User12 = { name: string };
function parse12(text: string): User12 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User12; }
```

### Regression tests

```typescript
console.assert(parse12('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-M-013: unsafe generic assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first13<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first13<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first13([1, 2]) === 1); console.assert(first13([]) === undefined);
```


## TS-M-014: missing required field

- Difficulty: Medium
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config14 = { retries: number; timeout: number };
const config14 = { retries: 3 } as Config14;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config14 = { retries: number; timeout: number };
function makeConfig14(input: Partial<Config14>): Config14 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config14 = makeConfig14({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config14.timeout === 1000);
```


## TS-M-015: property access before narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result15 = { ok: true; value: number } | { ok: false; error: string };
function message15(result: Result15): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result15 = { ok: true; value: number } | { ok: false; error: string };
function message15(result: Result15): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message15({ok: true, value: 0}) === '0');
```


## TS-M-016: implicit any

- Difficulty: Medium
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values16 = [1, 2, 3];
const doubled16 = values16.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values16: number[] = [1, 2, 3];
const doubled16: number[] = values16.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled16[2] === 6); // Regression: compile with strict enabled.
```


## TS-M-017: non-null assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get17(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get17(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get17(['a'], 2) === undefined);
```


## TS-M-018: forgotten Promise

- Difficulty: Medium
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay18(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay18(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay18(10).then(value => console.assert(value === 10));
```


## TS-M-019: unchecked indexed access

- Difficulty: Medium
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last19(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last19(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last19([4, 5]) === 5); console.assert(last19([]) === undefined);
```


## TS-M-020: enum or string mismatch

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode20 = 'fast' | 'safe';
function run20(mode: Mode20) { return mode.toUpperCase(); }
const input20 = 'debug' as Mode20;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode20 = 'fast' | 'safe';
function parseMode20(input: string): Mode20 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input20 = parseMode20('safe');
```

### Regression tests

```typescript
console.assert(input20 === 'safe'); // Regression: parseMode20('debug') throws.
```


## TS-M-021: truthiness narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count21(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count21(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count21(0) === 'present'); console.assert(count21(undefined) === 'missing');
```


## TS-M-022: assertion is not validation

- Difficulty: Medium
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User22 = { name: string };
function parse22(text: string): User22 { return JSON.parse(text) as User22; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User22 = { name: string };
function parse22(text: string): User22 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User22; }
```

### Regression tests

```typescript
console.assert(parse22('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-M-023: unsafe generic assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first23<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first23<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first23([1, 2]) === 1); console.assert(first23([]) === undefined);
```


## TS-M-024: missing required field

- Difficulty: Medium
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config24 = { retries: number; timeout: number };
const config24 = { retries: 3 } as Config24;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config24 = { retries: number; timeout: number };
function makeConfig24(input: Partial<Config24>): Config24 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config24 = makeConfig24({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config24.timeout === 1000);
```


## TS-M-025: property access before narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result25 = { ok: true; value: number } | { ok: false; error: string };
function message25(result: Result25): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result25 = { ok: true; value: number } | { ok: false; error: string };
function message25(result: Result25): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message25({ok: true, value: 0}) === '0');
```


## TS-M-026: implicit any

- Difficulty: Medium
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values26 = [1, 2, 3];
const doubled26 = values26.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values26: number[] = [1, 2, 3];
const doubled26: number[] = values26.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled26[2] === 6); // Regression: compile with strict enabled.
```


## TS-M-027: non-null assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get27(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get27(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get27(['a'], 2) === undefined);
```


## TS-M-028: forgotten Promise

- Difficulty: Medium
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay28(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay28(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay28(10).then(value => console.assert(value === 10));
```


## TS-M-029: unchecked indexed access

- Difficulty: Medium
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last29(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last29(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last29([4, 5]) === 5); console.assert(last29([]) === undefined);
```


## TS-M-030: enum or string mismatch

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode30 = 'fast' | 'safe';
function run30(mode: Mode30) { return mode.toUpperCase(); }
const input30 = 'debug' as Mode30;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode30 = 'fast' | 'safe';
function parseMode30(input: string): Mode30 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input30 = parseMode30('safe');
```

### Regression tests

```typescript
console.assert(input30 === 'safe'); // Regression: parseMode30('debug') throws.
```


## TS-M-031: truthiness narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count31(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count31(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count31(0) === 'present'); console.assert(count31(undefined) === 'missing');
```


## TS-M-032: assertion is not validation

- Difficulty: Medium
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User32 = { name: string };
function parse32(text: string): User32 { return JSON.parse(text) as User32; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User32 = { name: string };
function parse32(text: string): User32 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User32; }
```

### Regression tests

```typescript
console.assert(parse32('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-M-033: unsafe generic assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first33<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first33<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first33([1, 2]) === 1); console.assert(first33([]) === undefined);
```


## TS-M-034: missing required field

- Difficulty: Medium
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config34 = { retries: number; timeout: number };
const config34 = { retries: 3 } as Config34;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config34 = { retries: number; timeout: number };
function makeConfig34(input: Partial<Config34>): Config34 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config34 = makeConfig34({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config34.timeout === 1000);
```


## TS-M-035: property access before narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result35 = { ok: true; value: number } | { ok: false; error: string };
function message35(result: Result35): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result35 = { ok: true; value: number } | { ok: false; error: string };
function message35(result: Result35): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message35({ok: true, value: 0}) === '0');
```


## TS-M-036: implicit any

- Difficulty: Medium
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values36 = [1, 2, 3];
const doubled36 = values36.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values36: number[] = [1, 2, 3];
const doubled36: number[] = values36.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled36[2] === 6); // Regression: compile with strict enabled.
```


## TS-M-037: non-null assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get37(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get37(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get37(['a'], 2) === undefined);
```


## TS-M-038: forgotten Promise

- Difficulty: Medium
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay38(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay38(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay38(10).then(value => console.assert(value === 10));
```


## TS-M-039: unchecked indexed access

- Difficulty: Medium
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last39(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last39(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last39([4, 5]) === 5); console.assert(last39([]) === undefined);
```


## TS-M-040: enum or string mismatch

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode40 = 'fast' | 'safe';
function run40(mode: Mode40) { return mode.toUpperCase(); }
const input40 = 'debug' as Mode40;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode40 = 'fast' | 'safe';
function parseMode40(input: string): Mode40 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input40 = parseMode40('safe');
```

### Regression tests

```typescript
console.assert(input40 === 'safe'); // Regression: parseMode40('debug') throws.
```


## TS-M-041: truthiness narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count41(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count41(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count41(0) === 'present'); console.assert(count41(undefined) === 'missing');
```


## TS-M-042: assertion is not validation

- Difficulty: Medium
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User42 = { name: string };
function parse42(text: string): User42 { return JSON.parse(text) as User42; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User42 = { name: string };
function parse42(text: string): User42 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User42; }
```

### Regression tests

```typescript
console.assert(parse42('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-M-043: unsafe generic assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first43<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first43<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first43([1, 2]) === 1); console.assert(first43([]) === undefined);
```


## TS-M-044: missing required field

- Difficulty: Medium
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config44 = { retries: number; timeout: number };
const config44 = { retries: 3 } as Config44;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config44 = { retries: number; timeout: number };
function makeConfig44(input: Partial<Config44>): Config44 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config44 = makeConfig44({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config44.timeout === 1000);
```


## TS-M-045: property access before narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result45 = { ok: true; value: number } | { ok: false; error: string };
function message45(result: Result45): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result45 = { ok: true; value: number } | { ok: false; error: string };
function message45(result: Result45): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message45({ok: true, value: 0}) === '0');
```


## TS-M-046: implicit any

- Difficulty: Medium
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values46 = [1, 2, 3];
const doubled46 = values46.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values46: number[] = [1, 2, 3];
const doubled46: number[] = values46.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled46[2] === 6); // Regression: compile with strict enabled.
```


## TS-M-047: non-null assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get47(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get47(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get47(['a'], 2) === undefined);
```


## TS-M-048: forgotten Promise

- Difficulty: Medium
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay48(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay48(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay48(10).then(value => console.assert(value === 10));
```


## TS-M-049: unchecked indexed access

- Difficulty: Medium
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last49(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last49(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last49([4, 5]) === 5); console.assert(last49([]) === undefined);
```


## TS-M-050: enum or string mismatch

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode50 = 'fast' | 'safe';
function run50(mode: Mode50) { return mode.toUpperCase(); }
const input50 = 'debug' as Mode50;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode50 = 'fast' | 'safe';
function parseMode50(input: string): Mode50 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input50 = parseMode50('safe');
```

### Regression tests

```typescript
console.assert(input50 === 'safe'); // Regression: parseMode50('debug') throws.
```


## TS-M-051: truthiness narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count51(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count51(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count51(0) === 'present'); console.assert(count51(undefined) === 'missing');
```


## TS-M-052: assertion is not validation

- Difficulty: Medium
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User52 = { name: string };
function parse52(text: string): User52 { return JSON.parse(text) as User52; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User52 = { name: string };
function parse52(text: string): User52 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User52; }
```

### Regression tests

```typescript
console.assert(parse52('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-M-053: unsafe generic assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first53<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first53<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first53([1, 2]) === 1); console.assert(first53([]) === undefined);
```


## TS-M-054: missing required field

- Difficulty: Medium
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config54 = { retries: number; timeout: number };
const config54 = { retries: 3 } as Config54;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config54 = { retries: number; timeout: number };
function makeConfig54(input: Partial<Config54>): Config54 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config54 = makeConfig54({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config54.timeout === 1000);
```


## TS-M-055: property access before narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result55 = { ok: true; value: number } | { ok: false; error: string };
function message55(result: Result55): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result55 = { ok: true; value: number } | { ok: false; error: string };
function message55(result: Result55): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message55({ok: true, value: 0}) === '0');
```


## TS-M-056: implicit any

- Difficulty: Medium
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values56 = [1, 2, 3];
const doubled56 = values56.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values56: number[] = [1, 2, 3];
const doubled56: number[] = values56.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled56[2] === 6); // Regression: compile with strict enabled.
```


## TS-M-057: non-null assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get57(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get57(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get57(['a'], 2) === undefined);
```


## TS-M-058: forgotten Promise

- Difficulty: Medium
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay58(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay58(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay58(10).then(value => console.assert(value === 10));
```


## TS-M-059: unchecked indexed access

- Difficulty: Medium
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last59(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last59(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last59([4, 5]) === 5); console.assert(last59([]) === undefined);
```


## TS-M-060: enum or string mismatch

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode60 = 'fast' | 'safe';
function run60(mode: Mode60) { return mode.toUpperCase(); }
const input60 = 'debug' as Mode60;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode60 = 'fast' | 'safe';
function parseMode60(input: string): Mode60 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input60 = parseMode60('safe');
```

### Regression tests

```typescript
console.assert(input60 === 'safe'); // Regression: parseMode60('debug') throws.
```


## TS-M-061: truthiness narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count61(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count61(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count61(0) === 'present'); console.assert(count61(undefined) === 'missing');
```


## TS-M-062: assertion is not validation

- Difficulty: Medium
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User62 = { name: string };
function parse62(text: string): User62 { return JSON.parse(text) as User62; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User62 = { name: string };
function parse62(text: string): User62 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User62; }
```

### Regression tests

```typescript
console.assert(parse62('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-M-063: unsafe generic assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first63<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first63<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first63([1, 2]) === 1); console.assert(first63([]) === undefined);
```


## TS-M-064: missing required field

- Difficulty: Medium
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config64 = { retries: number; timeout: number };
const config64 = { retries: 3 } as Config64;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config64 = { retries: number; timeout: number };
function makeConfig64(input: Partial<Config64>): Config64 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config64 = makeConfig64({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config64.timeout === 1000);
```


## TS-M-065: property access before narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result65 = { ok: true; value: number } | { ok: false; error: string };
function message65(result: Result65): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result65 = { ok: true; value: number } | { ok: false; error: string };
function message65(result: Result65): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message65({ok: true, value: 0}) === '0');
```


## TS-M-066: implicit any

- Difficulty: Medium
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values66 = [1, 2, 3];
const doubled66 = values66.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values66: number[] = [1, 2, 3];
const doubled66: number[] = values66.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled66[2] === 6); // Regression: compile with strict enabled.
```


## TS-M-067: non-null assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get67(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get67(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get67(['a'], 2) === undefined);
```


## TS-M-068: forgotten Promise

- Difficulty: Medium
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay68(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay68(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay68(10).then(value => console.assert(value === 10));
```


## TS-M-069: unchecked indexed access

- Difficulty: Medium
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last69(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last69(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last69([4, 5]) === 5); console.assert(last69([]) === undefined);
```


## TS-M-070: enum or string mismatch

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode70 = 'fast' | 'safe';
function run70(mode: Mode70) { return mode.toUpperCase(); }
const input70 = 'debug' as Mode70;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode70 = 'fast' | 'safe';
function parseMode70(input: string): Mode70 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input70 = parseMode70('safe');
```

### Regression tests

```typescript
console.assert(input70 === 'safe'); // Regression: parseMode70('debug') throws.
```


## TS-M-071: truthiness narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count71(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count71(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count71(0) === 'present'); console.assert(count71(undefined) === 'missing');
```


## TS-M-072: assertion is not validation

- Difficulty: Medium
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User72 = { name: string };
function parse72(text: string): User72 { return JSON.parse(text) as User72; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User72 = { name: string };
function parse72(text: string): User72 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User72; }
```

### Regression tests

```typescript
console.assert(parse72('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-M-073: unsafe generic assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first73<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first73<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first73([1, 2]) === 1); console.assert(first73([]) === undefined);
```


## TS-M-074: missing required field

- Difficulty: Medium
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config74 = { retries: number; timeout: number };
const config74 = { retries: 3 } as Config74;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config74 = { retries: number; timeout: number };
function makeConfig74(input: Partial<Config74>): Config74 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config74 = makeConfig74({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config74.timeout === 1000);
```


## TS-M-075: property access before narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result75 = { ok: true; value: number } | { ok: false; error: string };
function message75(result: Result75): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result75 = { ok: true; value: number } | { ok: false; error: string };
function message75(result: Result75): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message75({ok: true, value: 0}) === '0');
```


## TS-M-076: implicit any

- Difficulty: Medium
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values76 = [1, 2, 3];
const doubled76 = values76.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values76: number[] = [1, 2, 3];
const doubled76: number[] = values76.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled76[2] === 6); // Regression: compile with strict enabled.
```


## TS-M-077: non-null assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get77(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get77(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get77(['a'], 2) === undefined);
```


## TS-M-078: forgotten Promise

- Difficulty: Medium
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay78(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay78(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay78(10).then(value => console.assert(value === 10));
```


## TS-M-079: unchecked indexed access

- Difficulty: Medium
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last79(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last79(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last79([4, 5]) === 5); console.assert(last79([]) === undefined);
```


## TS-M-080: enum or string mismatch

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode80 = 'fast' | 'safe';
function run80(mode: Mode80) { return mode.toUpperCase(); }
const input80 = 'debug' as Mode80;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode80 = 'fast' | 'safe';
function parseMode80(input: string): Mode80 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input80 = parseMode80('safe');
```

### Regression tests

```typescript
console.assert(input80 === 'safe'); // Regression: parseMode80('debug') throws.
```


## TS-M-081: truthiness narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count81(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count81(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count81(0) === 'present'); console.assert(count81(undefined) === 'missing');
```


## TS-M-082: assertion is not validation

- Difficulty: Medium
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User82 = { name: string };
function parse82(text: string): User82 { return JSON.parse(text) as User82; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User82 = { name: string };
function parse82(text: string): User82 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User82; }
```

### Regression tests

```typescript
console.assert(parse82('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-M-083: unsafe generic assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first83<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first83<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first83([1, 2]) === 1); console.assert(first83([]) === undefined);
```


## TS-M-084: missing required field

- Difficulty: Medium
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config84 = { retries: number; timeout: number };
const config84 = { retries: 3 } as Config84;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config84 = { retries: number; timeout: number };
function makeConfig84(input: Partial<Config84>): Config84 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config84 = makeConfig84({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config84.timeout === 1000);
```


## TS-M-085: property access before narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result85 = { ok: true; value: number } | { ok: false; error: string };
function message85(result: Result85): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result85 = { ok: true; value: number } | { ok: false; error: string };
function message85(result: Result85): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message85({ok: true, value: 0}) === '0');
```


## TS-M-086: implicit any

- Difficulty: Medium
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values86 = [1, 2, 3];
const doubled86 = values86.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values86: number[] = [1, 2, 3];
const doubled86: number[] = values86.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled86[2] === 6); // Regression: compile with strict enabled.
```


## TS-M-087: non-null assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get87(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get87(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get87(['a'], 2) === undefined);
```


## TS-M-088: forgotten Promise

- Difficulty: Medium
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay88(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay88(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay88(10).then(value => console.assert(value === 10));
```


## TS-M-089: unchecked indexed access

- Difficulty: Medium
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last89(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last89(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last89([4, 5]) === 5); console.assert(last89([]) === undefined);
```


## TS-M-090: enum or string mismatch

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode90 = 'fast' | 'safe';
function run90(mode: Mode90) { return mode.toUpperCase(); }
const input90 = 'debug' as Mode90;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode90 = 'fast' | 'safe';
function parseMode90(input: string): Mode90 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input90 = parseMode90('safe');
```

### Regression tests

```typescript
console.assert(input90 === 'safe'); // Regression: parseMode90('debug') throws.
```


## TS-M-091: truthiness narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count91(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count91(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count91(0) === 'present'); console.assert(count91(undefined) === 'missing');
```


## TS-M-092: assertion is not validation

- Difficulty: Medium
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User92 = { name: string };
function parse92(text: string): User92 { return JSON.parse(text) as User92; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User92 = { name: string };
function parse92(text: string): User92 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User92; }
```

### Regression tests

```typescript
console.assert(parse92('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-M-093: unsafe generic assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first93<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first93<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first93([1, 2]) === 1); console.assert(first93([]) === undefined);
```


## TS-M-094: missing required field

- Difficulty: Medium
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config94 = { retries: number; timeout: number };
const config94 = { retries: 3 } as Config94;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config94 = { retries: number; timeout: number };
function makeConfig94(input: Partial<Config94>): Config94 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config94 = makeConfig94({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config94.timeout === 1000);
```


## TS-M-095: property access before narrowing

- Difficulty: Medium
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result95 = { ok: true; value: number } | { ok: false; error: string };
function message95(result: Result95): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result95 = { ok: true; value: number } | { ok: false; error: string };
function message95(result: Result95): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message95({ok: true, value: 0}) === '0');
```


## TS-M-096: implicit any

- Difficulty: Medium
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values96 = [1, 2, 3];
const doubled96 = values96.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values96: number[] = [1, 2, 3];
const doubled96: number[] = values96.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled96[2] === 6); // Regression: compile with strict enabled.
```


## TS-M-097: non-null assertion

- Difficulty: Medium
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get97(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get97(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get97(['a'], 2) === undefined);
```


## TS-M-098: forgotten Promise

- Difficulty: Medium
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay98(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay98(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay98(10).then(value => console.assert(value === 10));
```


## TS-M-099: unchecked indexed access

- Difficulty: Medium
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last99(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last99(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last99([4, 5]) === 5); console.assert(last99([]) === undefined);
```


## TS-M-100: enum or string mismatch

- Difficulty: Medium
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode100 = 'fast' | 'safe';
function run100(mode: Mode100) { return mode.toUpperCase(); }
const input100 = 'debug' as Mode100;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode100 = 'fast' | 'safe';
function parseMode100(input: string): Mode100 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input100 = parseMode100('safe');
```

### Regression tests

```typescript
console.assert(input100 === 'safe'); // Regression: parseMode100('debug') throws.
```


## TS-H-001: truthiness narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count1(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count1(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count1(0) === 'present'); console.assert(count1(undefined) === 'missing');
```


## TS-H-002: assertion is not validation

- Difficulty: Hard
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User2 = { name: string };
function parse2(text: string): User2 { return JSON.parse(text) as User2; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User2 = { name: string };
function parse2(text: string): User2 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User2; }
```

### Regression tests

```typescript
console.assert(parse2('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-H-003: unsafe generic assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first3<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first3<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first3([1, 2]) === 1); console.assert(first3([]) === undefined);
```


## TS-H-004: missing required field

- Difficulty: Hard
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config4 = { retries: number; timeout: number };
const config4 = { retries: 3 } as Config4;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config4 = { retries: number; timeout: number };
function makeConfig4(input: Partial<Config4>): Config4 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config4 = makeConfig4({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config4.timeout === 1000);
```


## TS-H-005: property access before narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result5 = { ok: true; value: number } | { ok: false; error: string };
function message5(result: Result5): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result5 = { ok: true; value: number } | { ok: false; error: string };
function message5(result: Result5): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message5({ok: true, value: 0}) === '0');
```


## TS-H-006: implicit any

- Difficulty: Hard
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values6 = [1, 2, 3];
const doubled6 = values6.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values6: number[] = [1, 2, 3];
const doubled6: number[] = values6.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled6[2] === 6); // Regression: compile with strict enabled.
```


## TS-H-007: non-null assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get7(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get7(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get7(['a'], 2) === undefined);
```


## TS-H-008: forgotten Promise

- Difficulty: Hard
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay8(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay8(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay8(10).then(value => console.assert(value === 10));
```


## TS-H-009: unchecked indexed access

- Difficulty: Hard
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last9(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last9(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last9([4, 5]) === 5); console.assert(last9([]) === undefined);
```


## TS-H-010: enum or string mismatch

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode10 = 'fast' | 'safe';
function run10(mode: Mode10) { return mode.toUpperCase(); }
const input10 = 'debug' as Mode10;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode10 = 'fast' | 'safe';
function parseMode10(input: string): Mode10 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input10 = parseMode10('safe');
```

### Regression tests

```typescript
console.assert(input10 === 'safe'); // Regression: parseMode10('debug') throws.
```


## TS-H-011: truthiness narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count11(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count11(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count11(0) === 'present'); console.assert(count11(undefined) === 'missing');
```


## TS-H-012: assertion is not validation

- Difficulty: Hard
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User12 = { name: string };
function parse12(text: string): User12 { return JSON.parse(text) as User12; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User12 = { name: string };
function parse12(text: string): User12 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User12; }
```

### Regression tests

```typescript
console.assert(parse12('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-H-013: unsafe generic assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first13<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first13<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first13([1, 2]) === 1); console.assert(first13([]) === undefined);
```


## TS-H-014: missing required field

- Difficulty: Hard
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config14 = { retries: number; timeout: number };
const config14 = { retries: 3 } as Config14;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config14 = { retries: number; timeout: number };
function makeConfig14(input: Partial<Config14>): Config14 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config14 = makeConfig14({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config14.timeout === 1000);
```


## TS-H-015: property access before narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result15 = { ok: true; value: number } | { ok: false; error: string };
function message15(result: Result15): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result15 = { ok: true; value: number } | { ok: false; error: string };
function message15(result: Result15): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message15({ok: true, value: 0}) === '0');
```


## TS-H-016: implicit any

- Difficulty: Hard
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values16 = [1, 2, 3];
const doubled16 = values16.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values16: number[] = [1, 2, 3];
const doubled16: number[] = values16.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled16[2] === 6); // Regression: compile with strict enabled.
```


## TS-H-017: non-null assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get17(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get17(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get17(['a'], 2) === undefined);
```


## TS-H-018: forgotten Promise

- Difficulty: Hard
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay18(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay18(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay18(10).then(value => console.assert(value === 10));
```


## TS-H-019: unchecked indexed access

- Difficulty: Hard
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last19(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last19(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last19([4, 5]) === 5); console.assert(last19([]) === undefined);
```


## TS-H-020: enum or string mismatch

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode20 = 'fast' | 'safe';
function run20(mode: Mode20) { return mode.toUpperCase(); }
const input20 = 'debug' as Mode20;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode20 = 'fast' | 'safe';
function parseMode20(input: string): Mode20 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input20 = parseMode20('safe');
```

### Regression tests

```typescript
console.assert(input20 === 'safe'); // Regression: parseMode20('debug') throws.
```


## TS-H-021: truthiness narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count21(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count21(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count21(0) === 'present'); console.assert(count21(undefined) === 'missing');
```


## TS-H-022: assertion is not validation

- Difficulty: Hard
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User22 = { name: string };
function parse22(text: string): User22 { return JSON.parse(text) as User22; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User22 = { name: string };
function parse22(text: string): User22 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User22; }
```

### Regression tests

```typescript
console.assert(parse22('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-H-023: unsafe generic assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first23<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first23<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first23([1, 2]) === 1); console.assert(first23([]) === undefined);
```


## TS-H-024: missing required field

- Difficulty: Hard
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config24 = { retries: number; timeout: number };
const config24 = { retries: 3 } as Config24;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config24 = { retries: number; timeout: number };
function makeConfig24(input: Partial<Config24>): Config24 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config24 = makeConfig24({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config24.timeout === 1000);
```


## TS-H-025: property access before narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result25 = { ok: true; value: number } | { ok: false; error: string };
function message25(result: Result25): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result25 = { ok: true; value: number } | { ok: false; error: string };
function message25(result: Result25): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message25({ok: true, value: 0}) === '0');
```


## TS-H-026: implicit any

- Difficulty: Hard
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values26 = [1, 2, 3];
const doubled26 = values26.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values26: number[] = [1, 2, 3];
const doubled26: number[] = values26.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled26[2] === 6); // Regression: compile with strict enabled.
```


## TS-H-027: non-null assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get27(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get27(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get27(['a'], 2) === undefined);
```


## TS-H-028: forgotten Promise

- Difficulty: Hard
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay28(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay28(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay28(10).then(value => console.assert(value === 10));
```


## TS-H-029: unchecked indexed access

- Difficulty: Hard
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last29(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last29(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last29([4, 5]) === 5); console.assert(last29([]) === undefined);
```


## TS-H-030: enum or string mismatch

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode30 = 'fast' | 'safe';
function run30(mode: Mode30) { return mode.toUpperCase(); }
const input30 = 'debug' as Mode30;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode30 = 'fast' | 'safe';
function parseMode30(input: string): Mode30 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input30 = parseMode30('safe');
```

### Regression tests

```typescript
console.assert(input30 === 'safe'); // Regression: parseMode30('debug') throws.
```


## TS-H-031: truthiness narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count31(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count31(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count31(0) === 'present'); console.assert(count31(undefined) === 'missing');
```


## TS-H-032: assertion is not validation

- Difficulty: Hard
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User32 = { name: string };
function parse32(text: string): User32 { return JSON.parse(text) as User32; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User32 = { name: string };
function parse32(text: string): User32 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User32; }
```

### Regression tests

```typescript
console.assert(parse32('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-H-033: unsafe generic assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first33<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first33<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first33([1, 2]) === 1); console.assert(first33([]) === undefined);
```


## TS-H-034: missing required field

- Difficulty: Hard
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config34 = { retries: number; timeout: number };
const config34 = { retries: 3 } as Config34;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config34 = { retries: number; timeout: number };
function makeConfig34(input: Partial<Config34>): Config34 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config34 = makeConfig34({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config34.timeout === 1000);
```


## TS-H-035: property access before narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result35 = { ok: true; value: number } | { ok: false; error: string };
function message35(result: Result35): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result35 = { ok: true; value: number } | { ok: false; error: string };
function message35(result: Result35): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message35({ok: true, value: 0}) === '0');
```


## TS-H-036: implicit any

- Difficulty: Hard
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values36 = [1, 2, 3];
const doubled36 = values36.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values36: number[] = [1, 2, 3];
const doubled36: number[] = values36.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled36[2] === 6); // Regression: compile with strict enabled.
```


## TS-H-037: non-null assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get37(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get37(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get37(['a'], 2) === undefined);
```


## TS-H-038: forgotten Promise

- Difficulty: Hard
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay38(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay38(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay38(10).then(value => console.assert(value === 10));
```


## TS-H-039: unchecked indexed access

- Difficulty: Hard
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last39(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last39(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last39([4, 5]) === 5); console.assert(last39([]) === undefined);
```


## TS-H-040: enum or string mismatch

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode40 = 'fast' | 'safe';
function run40(mode: Mode40) { return mode.toUpperCase(); }
const input40 = 'debug' as Mode40;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode40 = 'fast' | 'safe';
function parseMode40(input: string): Mode40 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input40 = parseMode40('safe');
```

### Regression tests

```typescript
console.assert(input40 === 'safe'); // Regression: parseMode40('debug') throws.
```


## TS-H-041: truthiness narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count41(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count41(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count41(0) === 'present'); console.assert(count41(undefined) === 'missing');
```


## TS-H-042: assertion is not validation

- Difficulty: Hard
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User42 = { name: string };
function parse42(text: string): User42 { return JSON.parse(text) as User42; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User42 = { name: string };
function parse42(text: string): User42 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User42; }
```

### Regression tests

```typescript
console.assert(parse42('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-H-043: unsafe generic assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first43<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first43<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first43([1, 2]) === 1); console.assert(first43([]) === undefined);
```


## TS-H-044: missing required field

- Difficulty: Hard
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config44 = { retries: number; timeout: number };
const config44 = { retries: 3 } as Config44;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config44 = { retries: number; timeout: number };
function makeConfig44(input: Partial<Config44>): Config44 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config44 = makeConfig44({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config44.timeout === 1000);
```


## TS-H-045: property access before narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result45 = { ok: true; value: number } | { ok: false; error: string };
function message45(result: Result45): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result45 = { ok: true; value: number } | { ok: false; error: string };
function message45(result: Result45): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message45({ok: true, value: 0}) === '0');
```


## TS-H-046: implicit any

- Difficulty: Hard
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values46 = [1, 2, 3];
const doubled46 = values46.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values46: number[] = [1, 2, 3];
const doubled46: number[] = values46.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled46[2] === 6); // Regression: compile with strict enabled.
```


## TS-H-047: non-null assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get47(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get47(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get47(['a'], 2) === undefined);
```


## TS-H-048: forgotten Promise

- Difficulty: Hard
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay48(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay48(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay48(10).then(value => console.assert(value === 10));
```


## TS-H-049: unchecked indexed access

- Difficulty: Hard
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last49(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last49(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last49([4, 5]) === 5); console.assert(last49([]) === undefined);
```


## TS-H-050: enum or string mismatch

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode50 = 'fast' | 'safe';
function run50(mode: Mode50) { return mode.toUpperCase(); }
const input50 = 'debug' as Mode50;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode50 = 'fast' | 'safe';
function parseMode50(input: string): Mode50 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input50 = parseMode50('safe');
```

### Regression tests

```typescript
console.assert(input50 === 'safe'); // Regression: parseMode50('debug') throws.
```


## TS-H-051: truthiness narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count51(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count51(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count51(0) === 'present'); console.assert(count51(undefined) === 'missing');
```


## TS-H-052: assertion is not validation

- Difficulty: Hard
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User52 = { name: string };
function parse52(text: string): User52 { return JSON.parse(text) as User52; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User52 = { name: string };
function parse52(text: string): User52 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User52; }
```

### Regression tests

```typescript
console.assert(parse52('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-H-053: unsafe generic assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first53<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first53<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first53([1, 2]) === 1); console.assert(first53([]) === undefined);
```


## TS-H-054: missing required field

- Difficulty: Hard
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config54 = { retries: number; timeout: number };
const config54 = { retries: 3 } as Config54;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config54 = { retries: number; timeout: number };
function makeConfig54(input: Partial<Config54>): Config54 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config54 = makeConfig54({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config54.timeout === 1000);
```


## TS-H-055: property access before narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result55 = { ok: true; value: number } | { ok: false; error: string };
function message55(result: Result55): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result55 = { ok: true; value: number } | { ok: false; error: string };
function message55(result: Result55): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message55({ok: true, value: 0}) === '0');
```


## TS-H-056: implicit any

- Difficulty: Hard
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values56 = [1, 2, 3];
const doubled56 = values56.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values56: number[] = [1, 2, 3];
const doubled56: number[] = values56.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled56[2] === 6); // Regression: compile with strict enabled.
```


## TS-H-057: non-null assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get57(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get57(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get57(['a'], 2) === undefined);
```


## TS-H-058: forgotten Promise

- Difficulty: Hard
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay58(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay58(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay58(10).then(value => console.assert(value === 10));
```


## TS-H-059: unchecked indexed access

- Difficulty: Hard
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last59(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last59(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last59([4, 5]) === 5); console.assert(last59([]) === undefined);
```


## TS-H-060: enum or string mismatch

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode60 = 'fast' | 'safe';
function run60(mode: Mode60) { return mode.toUpperCase(); }
const input60 = 'debug' as Mode60;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode60 = 'fast' | 'safe';
function parseMode60(input: string): Mode60 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input60 = parseMode60('safe');
```

### Regression tests

```typescript
console.assert(input60 === 'safe'); // Regression: parseMode60('debug') throws.
```


## TS-H-061: truthiness narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count61(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count61(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count61(0) === 'present'); console.assert(count61(undefined) === 'missing');
```


## TS-H-062: assertion is not validation

- Difficulty: Hard
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User62 = { name: string };
function parse62(text: string): User62 { return JSON.parse(text) as User62; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User62 = { name: string };
function parse62(text: string): User62 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User62; }
```

### Regression tests

```typescript
console.assert(parse62('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-H-063: unsafe generic assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first63<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first63<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first63([1, 2]) === 1); console.assert(first63([]) === undefined);
```


## TS-H-064: missing required field

- Difficulty: Hard
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config64 = { retries: number; timeout: number };
const config64 = { retries: 3 } as Config64;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config64 = { retries: number; timeout: number };
function makeConfig64(input: Partial<Config64>): Config64 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config64 = makeConfig64({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config64.timeout === 1000);
```


## TS-H-065: property access before narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result65 = { ok: true; value: number } | { ok: false; error: string };
function message65(result: Result65): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result65 = { ok: true; value: number } | { ok: false; error: string };
function message65(result: Result65): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message65({ok: true, value: 0}) === '0');
```


## TS-H-066: implicit any

- Difficulty: Hard
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values66 = [1, 2, 3];
const doubled66 = values66.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values66: number[] = [1, 2, 3];
const doubled66: number[] = values66.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled66[2] === 6); // Regression: compile with strict enabled.
```


## TS-H-067: non-null assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get67(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get67(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get67(['a'], 2) === undefined);
```


## TS-H-068: forgotten Promise

- Difficulty: Hard
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay68(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay68(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay68(10).then(value => console.assert(value === 10));
```


## TS-H-069: unchecked indexed access

- Difficulty: Hard
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last69(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last69(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last69([4, 5]) === 5); console.assert(last69([]) === undefined);
```


## TS-H-070: enum or string mismatch

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode70 = 'fast' | 'safe';
function run70(mode: Mode70) { return mode.toUpperCase(); }
const input70 = 'debug' as Mode70;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode70 = 'fast' | 'safe';
function parseMode70(input: string): Mode70 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input70 = parseMode70('safe');
```

### Regression tests

```typescript
console.assert(input70 === 'safe'); // Regression: parseMode70('debug') throws.
```


## TS-H-071: truthiness narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count71(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count71(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count71(0) === 'present'); console.assert(count71(undefined) === 'missing');
```


## TS-H-072: assertion is not validation

- Difficulty: Hard
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User72 = { name: string };
function parse72(text: string): User72 { return JSON.parse(text) as User72; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User72 = { name: string };
function parse72(text: string): User72 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User72; }
```

### Regression tests

```typescript
console.assert(parse72('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-H-073: unsafe generic assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first73<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first73<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first73([1, 2]) === 1); console.assert(first73([]) === undefined);
```


## TS-H-074: missing required field

- Difficulty: Hard
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config74 = { retries: number; timeout: number };
const config74 = { retries: 3 } as Config74;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config74 = { retries: number; timeout: number };
function makeConfig74(input: Partial<Config74>): Config74 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config74 = makeConfig74({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config74.timeout === 1000);
```


## TS-H-075: property access before narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result75 = { ok: true; value: number } | { ok: false; error: string };
function message75(result: Result75): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result75 = { ok: true; value: number } | { ok: false; error: string };
function message75(result: Result75): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message75({ok: true, value: 0}) === '0');
```


## TS-H-076: implicit any

- Difficulty: Hard
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values76 = [1, 2, 3];
const doubled76 = values76.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values76: number[] = [1, 2, 3];
const doubled76: number[] = values76.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled76[2] === 6); // Regression: compile with strict enabled.
```


## TS-H-077: non-null assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get77(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get77(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get77(['a'], 2) === undefined);
```


## TS-H-078: forgotten Promise

- Difficulty: Hard
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay78(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay78(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay78(10).then(value => console.assert(value === 10));
```


## TS-H-079: unchecked indexed access

- Difficulty: Hard
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last79(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last79(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last79([4, 5]) === 5); console.assert(last79([]) === undefined);
```


## TS-H-080: enum or string mismatch

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode80 = 'fast' | 'safe';
function run80(mode: Mode80) { return mode.toUpperCase(); }
const input80 = 'debug' as Mode80;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode80 = 'fast' | 'safe';
function parseMode80(input: string): Mode80 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input80 = parseMode80('safe');
```

### Regression tests

```typescript
console.assert(input80 === 'safe'); // Regression: parseMode80('debug') throws.
```


## TS-H-081: truthiness narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count81(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count81(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count81(0) === 'present'); console.assert(count81(undefined) === 'missing');
```


## TS-H-082: assertion is not validation

- Difficulty: Hard
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User82 = { name: string };
function parse82(text: string): User82 { return JSON.parse(text) as User82; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User82 = { name: string };
function parse82(text: string): User82 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User82; }
```

### Regression tests

```typescript
console.assert(parse82('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-H-083: unsafe generic assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first83<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first83<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first83([1, 2]) === 1); console.assert(first83([]) === undefined);
```


## TS-H-084: missing required field

- Difficulty: Hard
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config84 = { retries: number; timeout: number };
const config84 = { retries: 3 } as Config84;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config84 = { retries: number; timeout: number };
function makeConfig84(input: Partial<Config84>): Config84 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config84 = makeConfig84({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config84.timeout === 1000);
```


## TS-H-085: property access before narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result85 = { ok: true; value: number } | { ok: false; error: string };
function message85(result: Result85): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result85 = { ok: true; value: number } | { ok: false; error: string };
function message85(result: Result85): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message85({ok: true, value: 0}) === '0');
```


## TS-H-086: implicit any

- Difficulty: Hard
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values86 = [1, 2, 3];
const doubled86 = values86.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values86: number[] = [1, 2, 3];
const doubled86: number[] = values86.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled86[2] === 6); // Regression: compile with strict enabled.
```


## TS-H-087: non-null assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get87(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get87(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get87(['a'], 2) === undefined);
```


## TS-H-088: forgotten Promise

- Difficulty: Hard
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay88(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay88(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay88(10).then(value => console.assert(value === 10));
```


## TS-H-089: unchecked indexed access

- Difficulty: Hard
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last89(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last89(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last89([4, 5]) === 5); console.assert(last89([]) === undefined);
```


## TS-H-090: enum or string mismatch

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode90 = 'fast' | 'safe';
function run90(mode: Mode90) { return mode.toUpperCase(); }
const input90 = 'debug' as Mode90;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode90 = 'fast' | 'safe';
function parseMode90(input: string): Mode90 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input90 = parseMode90('safe');
```

### Regression tests

```typescript
console.assert(input90 === 'safe'); // Regression: parseMode90('debug') throws.
```


## TS-H-091: truthiness narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type reasoning
- Concept: truthiness narrowing
- Symptom: A valid zero is handled as missing.
- Diagnostic goal: Explain why truthiness is weaker than an explicit narrowing check.

### Buggy code

```typescript
function count91(value: number | undefined): string { return value ? 'present' : 'missing'; }
```

### Expected diagnosis

TypeScript narrows undefined away, but 0 is also falsy at runtime.

### Corrected code

```typescript
function count91(value: number | undefined): string { return value === undefined ? 'missing' : 'present'; }
```

### Regression tests

```typescript
console.assert(count91(0) === 'present'); console.assert(count91(undefined) === 'missing');
```


## TS-H-092: assertion is not validation

- Difficulty: Hard
- Language: TypeScript
- Perspective: Runtime boundary
- Concept: assertion is not validation
- Symptom: Malformed JSON passes the compiler and fails at runtime.
- Diagnostic goal: Separate static types from runtime evidence.

### Buggy code

```typescript
type User92 = { name: string };
function parse92(text: string): User92 { return JSON.parse(text) as User92; }
```

### Expected diagnosis

The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.

### Corrected code

```typescript
type User92 = { name: string };
function parse92(text: string): User92 { const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User92; }
```

### Regression tests

```typescript
console.assert(parse92('{"name":"Ada"}').name === 'Ada'); // Regression: reject '{}'.
```


## TS-H-093: unsafe generic assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Generic contract
- Concept: unsafe generic assertion
- Symptom: The function returns the wrong value while appearing type-safe.
- Diagnostic goal: Check whether the generic type is inferred from evidence or asserted by the caller.

### Buggy code

```typescript
function first93<T>(items: T[]): T { return items[0] as T; }
```

### Expected diagnosis

A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.

### Corrected code

```typescript
function first93<T>(items: T[]): T | undefined { return items[0]; }
```

### Regression tests

```typescript
console.assert(first93([1, 2]) === 1); console.assert(first93([]) === undefined);
```


## TS-H-094: missing required field

- Difficulty: Hard
- Language: TypeScript
- Perspective: Structural typing
- Concept: missing required field
- Symptom: A partial object is accepted through an unsafe assertion.
- Diagnostic goal: Distinguish structural compatibility from a runtime contract.

### Buggy code

```typescript
type Config94 = { retries: number; timeout: number };
const config94 = { retries: 3 } as Config94;
```

### Expected diagnosis

A type assertion suppresses the missing-property error; it does not add timeout at runtime.

### Corrected code

```typescript
type Config94 = { retries: number; timeout: number };
function makeConfig94(input: Partial<Config94>): Config94 { return { retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }; }
const config94 = makeConfig94({ retries: 3 });
```

### Regression tests

```typescript
console.assert(config94.timeout === 1000);
```


## TS-H-095: property access before narrowing

- Difficulty: Hard
- Language: TypeScript
- Perspective: Discriminated union
- Concept: property access before narrowing
- Symptom: The compiler rejects or runtime code reads the wrong branch.
- Diagnostic goal: Narrow on the discriminant before reading branch-specific fields.

### Buggy code

```typescript
type Result95 = { ok: true; value: number } | { ok: false; error: string };
function message95(result: Result95): string { return String(result.value || result.error); }
```

### Expected diagnosis

The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.

### Corrected code

```typescript
type Result95 = { ok: true; value: number } | { ok: false; error: string };
function message95(result: Result95): string { return result.ok ? String(result.value) : result.error; }
```

### Regression tests

```typescript
console.assert(message95({ok: true, value: 0}) === '0');
```


## TS-H-096: implicit any

- Difficulty: Hard
- Language: TypeScript
- Perspective: Compiler configuration
- Concept: implicit any
- Symptom: A callback parameter escapes type checking.
- Diagnostic goal: Make the compiler prove callback inputs.

### Buggy code

```typescript
const values96 = [1, 2, 3];
const doubled96 = values96.map(value => value * 2);
```

### Expected diagnosis

With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.

### Corrected code

```typescript
const values96: number[] = [1, 2, 3];
const doubled96: number[] = values96.map((value: number): number => value * 2);
```

### Regression tests

```typescript
console.assert(doubled96[2] === 6); // Regression: compile with strict enabled.
```


## TS-H-097: non-null assertion

- Difficulty: Hard
- Language: TypeScript
- Perspective: Nullability
- Concept: non-null assertion
- Symptom: The program throws when an element is absent.
- Diagnostic goal: Do not replace a missing-value proof with !.

### Buggy code

```typescript
function get97(items: string[], index: number): string { return items[index]!; }
```

### Expected diagnosis

The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.

### Corrected code

```typescript
function get97(items: string[], index: number): string | undefined { return items[index]; }
```

### Regression tests

```typescript
console.assert(get97(['a'], 2) === undefined);
```


## TS-H-098: forgotten Promise

- Difficulty: Hard
- Language: TypeScript
- Perspective: Async types
- Concept: forgotten Promise
- Symptom: The declared return type does not match the asynchronous implementation.
- Diagnostic goal: Make the promise boundary explicit in both type and control flow.

### Buggy code

```typescript
async function delay98(ms: number): number { return ms; }
```

### Expected diagnosis

An async function always returns Promise<number>, never number.

### Corrected code

```typescript
async function delay98(ms: number): Promise<number> { return ms; }
```

### Regression tests

```typescript
delay98(10).then(value => console.assert(value === 10));
```


## TS-H-099: unchecked indexed access

- Difficulty: Hard
- Language: TypeScript
- Perspective: Index safety
- Concept: unchecked indexed access
- Symptom: The code treats a possibly missing element as definite.
- Diagnostic goal: Model lookup failure instead of hiding it with a cast.

### Buggy code

```typescript
function last99(items: number[]): number { return items[items.length - 1]; }
```

### Expected diagnosis

An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.

### Corrected code

```typescript
function last99(items: number[]): number | undefined { return items.at(-1); }
```

### Regression tests

```typescript
console.assert(last99([4, 5]) === 5); console.assert(last99([]) === undefined);
```


## TS-H-100: enum or string mismatch

- Difficulty: Hard
- Language: TypeScript
- Perspective: Type/runtime equality
- Concept: enum or string mismatch
- Symptom: A value from the runtime does not match the assumed literal type.
- Diagnostic goal: Validate external strings before treating them as a union.

### Buggy code

```typescript
type Mode100 = 'fast' | 'safe';
function run100(mode: Mode100) { return mode.toUpperCase(); }
const input100 = 'debug' as Mode100;
```

### Expected diagnosis

A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.

### Corrected code

```typescript
type Mode100 = 'fast' | 'safe';
function parseMode100(input: string): Mode100 { if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }
const input100 = parseMode100('safe');
```

### Regression tests

```typescript
console.assert(input100 === 'safe'); // Regression: parseMode100('debug') throws.
```
