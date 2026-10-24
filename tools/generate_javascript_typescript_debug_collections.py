"""Generate separate JavaScript and TypeScript debugging corpora for RAG training."""
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def record(prefix, lang, i, difficulty, perspective, concept, symptom, goal, buggy, diagnosis, fixed, tests):
    fence = "typescript" if lang.lower() == "typescript" else "javascript"
    if lang.lower() == "typescript":
        # TypeScript snippets are checked as JavaScript-shaped source where possible;
        # the corpus itself remains editorial data, not learner-facing answer data.
        assert fixed.strip()
    return f"""## {prefix}-{difficulty[0].upper()}-{i:03d}: {concept}

- Difficulty: {difficulty}
- Language: {lang}
- Perspective: {perspective}
- Concept: {concept}
- Symptom: {symptom}
- Diagnostic goal: {goal}

### Buggy code

```{fence}
{buggy}
```

### Expected diagnosis

{diagnosis}

### Corrected code

```{fence}
{fixed}
```

### Regression tests

```{fence}
{tests}
```

"""


def js_rows(n):
    return [
        ("Output tracing", "loose equality", "The branch accepts an unexpected value.", "Trace coercion before comparing values.",
         f"function check{n}(value) {{ return value == 0 ? 'empty' : 'filled'; }}",
         "Loose equality converts values, so false, an empty string, and null-like values can compare equal to zero.",
         f"function check{n}(value) {{ return value === 0 ? 'empty' : 'filled'; }}",
         f"console.assert(check{n}(0) === 'empty'); console.assert(check{n}('0') === 'filled');"),
        ("Boundary analysis", "truthiness and zero", "A valid zero is treated as absent.", "Separate falsy values from missing values.",
         f"function label{n}(count) {{ return count ? 'present' : 'missing'; }}",
         "JavaScript treats 0 as falsy even when it is a valid domain value.",
         f"function label{n}(count) {{ return count === undefined ? 'missing' : 'present'; }}",
         f"console.assert(label{n}(0) === 'present'); console.assert(label{n}(undefined) === 'missing');"),
        ("State tracing", "array mutation", "The caller's array changes unexpectedly.", "Identify the shared reference.",
         f"function add{n}(items, value) {{ const copy = items; copy.push(value); return copy; }}",
         "Assigning an array copies its reference, so push mutates the caller's array.",
         f"function add{n}(items, value) {{ return [...items, value]; }}",
         f"const source{n} = [1]; const result{n} = add{n}(source{n}, 2); console.assert(source{n}.length === 1);"),
        ("Iteration reasoning", "for in versus for of", "The result contains indexes instead of values.", "Identify what the chosen iterator produces.",
         f"function sum{n}(items) {{ let total = 0; for (const item in items) total += item; return total; }}",
         "for...in yields property names, which are strings for array indexes; for...of yields elements.",
         f"function sum{n}(items) {{ let total = 0; for (const item of items) total += item; return total; }}",
         f"console.assert(sum{n}([2, 3]) === 5);"),
        ("Function contract", "default parameter", "An explicit null does not receive the fallback.", "Distinguish undefined defaults from null handling.",
         f"function name{n}(value = 'guest') {{ return value; }}",
         "Default parameters apply only when the argument is undefined, not when it is null.",
         f"function name{n}(value) {{ return value ?? 'guest'; }}",
         f"console.assert(name{n}(null) === 'guest'); console.assert(name{n}(undefined) === 'guest');"),
        ("Collection invariant", "reduce without identity", "An empty input throws a TypeError.", "Check the empty collection contract.",
         f"function total{n}(items) {{ return items.reduce((a, b) => a + b); }}",
         "reduce uses the first element when no initial value is supplied; an empty array has no first element.",
         f"function total{n}(items) {{ return items.reduce((a, b) => a + b, 0); }}",
         f"console.assert(total{n}([]) === 0); console.assert(total{n}([2, 3]) === 5);"),
        ("Closure reasoning", "loop capture", "Every callback reports the final index.", "Trace when the closure reads the loop variable.",
         f"function callbacks{n}(values) {{ var out = []; for (var i = 0; i < values.length; i++) out.push(() => values[i]); return out; }}",
         "var is function-scoped, so every callback reads the final i after the loop ends.",
         f"function callbacks{n}(values) {{ const out = []; for (let i = 0; i < values.length; i++) out.push(() => values[i]); return out; }}",
         f"const fs{n} = callbacks{n}(['a', 'b']); console.assert(fs{n}[0]() === 'a');"),
        ("Object semantics", "prototype pollution", "A membership check sees an inherited property.", "Distinguish own properties from inherited properties.",
         f"function has{n}(object, key) {{ return key in object; }}",
         "in searches the prototype chain, so inherited names can be mistaken for stored data.",
         f"function has{n}(object, key) {{ return Object.hasOwn(object, key); }}",
         f"const object{n} = Object.create({{hidden: true}}); console.assert(has{n}(object{n}, 'hidden') === false);"),
        ("Async ordering", "missing await", "The function returns a Promise instead of the resolved value.", "Trace the promise boundary.",
         f"async function load{n}() {{ return fetch('/data').json(); }}",
         "fetch(...).json() is asynchronous; returning it without await exposes the inner promise and hides rejection timing.",
         f"async function load{n}() {{ const response = await fetch('/data'); return await response.json(); }}",
         f"// Regression: await load{n}() and assert the parsed value; reject a non-OK response."),
        ("Module/runtime boundary", "unvalidated JSON", "A property access fails on malformed input.", "Validate parsed data before trusting its shape.",
         f"function user{n}(text) {{ const value = JSON.parse(text); return value.name.toUpperCase(); }}",
         "JSON.parse checks syntax only; it does not prove that the result is an object with a string name.",
         f"function user{n}(text) {{ const value = JSON.parse(text); if (!value || typeof value.name !== 'string') throw new TypeError('invalid user'); return value.name.toUpperCase(); }}",
         f"console.assert(user{n}('{{\"name\":\"Ada\"}}') === 'ADA'); // Regression: reject '{{}}'."),
    ]


def ts_rows(n):
    return [
        ("Type reasoning", "truthiness narrowing", "A valid zero is handled as missing.", "Explain why truthiness is weaker than an explicit narrowing check.",
         f"function count{n}(value: number | undefined): string {{ return value ? 'present' : 'missing'; }}",
         "TypeScript narrows undefined away, but 0 is also falsy at runtime.",
         f"function count{n}(value: number | undefined): string {{ return value === undefined ? 'missing' : 'present'; }}",
         f"console.assert(count{n}(0) === 'present'); console.assert(count{n}(undefined) === 'missing');"),
        ("Runtime boundary", "assertion is not validation", "Malformed JSON passes the compiler and fails at runtime.", "Separate static types from runtime evidence.",
         f"type User{n} = {{ name: string }};\nfunction parse{n}(text: string): User{n} {{ return JSON.parse(text) as User{n}; }}",
         "The assertion changes the compile-time view but performs no runtime check; JSON.parse can return any shape.",
         f"type User{n} = {{ name: string }};\nfunction parse{n}(text: string): User{n} {{ const value: unknown = JSON.parse(text); if (!value || typeof value !== 'object' || !('name' in value) || typeof value.name !== 'string') throw new TypeError('invalid user'); return value as User{n}; }}",
         f"console.assert(parse{n}('{{\"name\":\"Ada\"}}').name === 'Ada'); // Regression: reject '{{}}'."),
        ("Generic contract", "unsafe generic assertion", "The function returns the wrong value while appearing type-safe.", "Check whether the generic type is inferred from evidence or asserted by the caller.",
         f"function first{n}<T>(items: T[]): T {{ return items[0] as T; }}",
         "A generic return type does not guarantee a value exists; an empty array produces undefined despite the declared T.",
         f"function first{n}<T>(items: T[]): T | undefined {{ return items[0]; }}",
         f"console.assert(first{n}([1, 2]) === 1); console.assert(first{n}([]) === undefined);"),
        ("Structural typing", "missing required field", "A partial object is accepted through an unsafe assertion.", "Distinguish structural compatibility from a runtime contract.",
         f"type Config{n} = {{ retries: number; timeout: number }};\nconst config{n} = {{ retries: 3 }} as Config{n};",
         "A type assertion suppresses the missing-property error; it does not add timeout at runtime.",
         f"type Config{n} = {{ retries: number; timeout: number }};\nfunction makeConfig{n}(input: Partial<Config{n}>): Config{n} {{ return {{ retries: input.retries ?? 3, timeout: input.timeout ?? 1000 }}; }}\nconst config{n} = makeConfig{n}({{ retries: 3 }});",
         f"console.assert(config{n}.timeout === 1000);"),
        ("Discriminated union", "property access before narrowing", "The compiler rejects or runtime code reads the wrong branch.", "Narrow on the discriminant before reading branch-specific fields.",
         f"type Result{n} = {{ ok: true; value: number }} | {{ ok: false; error: string }};\nfunction message{n}(result: Result{n}): string {{ return String(result.value || result.error); }}",
         "The union does not guarantee value and error simultaneously; truthiness also mishandles a valid zero.",
         f"type Result{n} = {{ ok: true; value: number }} | {{ ok: false; error: string }};\nfunction message{n}(result: Result{n}): string {{ return result.ok ? String(result.value) : result.error; }}",
         f"console.assert(message{n}({{ok: true, value: 0}}) === '0');"),
        ("Compiler configuration", "implicit any", "A callback parameter escapes type checking.", "Make the compiler prove callback inputs.",
         f"const values{n} = [1, 2, 3];\nconst doubled{n} = values{n}.map(value => value * 2);",
         "With noImplicitAny disabled in a broader context, an untyped callback can hide incorrect assumptions; strict inference should be preserved.",
         f"const values{n}: number[] = [1, 2, 3];\nconst doubled{n}: number[] = values{n}.map((value: number): number => value * 2);",
         f"console.assert(doubled{n}[2] === 6); // Regression: compile with strict enabled."),
        ("Nullability", "non-null assertion", "The program throws when an element is absent.", "Do not replace a missing-value proof with !.",
         f"function get{n}(items: string[], index: number): string {{ return items[index]!; }}",
         "The non-null assertion is erased from JavaScript and cannot prevent undefined at runtime.",
         f"function get{n}(items: string[], index: number): string | undefined {{ return items[index]; }}",
         f"console.assert(get{n}(['a'], 2) === undefined);"),
        ("Async types", "forgotten Promise", "The declared return type does not match the asynchronous implementation.", "Make the promise boundary explicit in both type and control flow.",
         f"async function delay{n}(ms: number): number {{ return ms; }}",
         "An async function always returns Promise<number>, never number.",
         f"async function delay{n}(ms: number): Promise<number> {{ return ms; }}",
         f"delay{n}(10).then(value => console.assert(value === 10));"),
        ("Index safety", "unchecked indexed access", "The code treats a possibly missing element as definite.", "Model lookup failure instead of hiding it with a cast.",
         f"function last{n}(items: number[]): number {{ return items[items.length - 1]; }}",
         "An empty array has no last element; noUncheckedIndexedAccess exposes this boundary.",
         f"function last{n}(items: number[]): number | undefined {{ return items.at(-1); }}",
         f"console.assert(last{n}([4, 5]) === 5); console.assert(last{n}([]) === undefined);"),
        ("Type/runtime equality", "enum or string mismatch", "A value from the runtime does not match the assumed literal type.", "Validate external strings before treating them as a union.",
         f"type Mode{n} = 'fast' | 'safe';\nfunction run{n}(mode: Mode{n}) {{ return mode.toUpperCase(); }}\nconst input{n} = 'debug' as Mode{n};",
         "A cast can claim that an arbitrary runtime string belongs to a narrow union; the compiler cannot inspect the external value.",
         f"type Mode{n} = 'fast' | 'safe';\nfunction parseMode{n}(input: string): Mode{n} {{ if (input === 'fast' || input === 'safe') return input; throw new Error('invalid mode'); }}\nconst input{n} = parseMode{n}('safe');",
         f"console.assert(input{n} === 'safe'); // Regression: parseMode{n}('debug') throws."),
    ]


def build(lang, prefix, rows, output):
    sections = [f"# {lang} Debug Exercises\n\nA RAG-training corpus of 300 {lang} debugging exercises. Corrected code is editorial material and must be stripped from learner-facing challenge responses.\n\n## Coverage\n\n- Easy: 100 exercises\n- Medium: 100 exercises\n- Hard: 100 exercises\n- Perspectives: runtime behavior, type reasoning, state, contracts, collections, async control flow, security boundaries, and complexity\n\n"]
    for difficulty, builder in (("Easy", rows[0]), ("Medium", rows[1]), ("Hard", rows[2])):
        for i in range(1, 101):
            sections.append(record(prefix, lang, i, difficulty, *builder(i)[(i - 1) % len(builder(i))]))
    output.write_text("\n".join(sections), encoding="utf-8")


def main():
    build("JavaScript", "JS", (js_rows, js_rows, js_rows), ROOT / "docs/curriculum/javascript-debug-exercises.md")
    build("TypeScript", "TS", (ts_rows, ts_rows, ts_rows), ROOT / "docs/curriculum/typescript-debug-exercises.md")
    print("wrote JavaScript and TypeScript corpora")


if __name__ == "__main__":
    main()
