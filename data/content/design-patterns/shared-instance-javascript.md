---
track: design-patterns
difficulty: Medium
language: javascript
patterns: singleton
category: Creational
source: authored
io_mode: function
---
# One Shared Instance in JavaScript — Medium — Creational

## The short answer
An ES module is already a singleton. The specification evaluates a module body
once per registry and caches the result; every `import` after the first gets
the same bindings.

```js
// db.js
export const pool = createPool(process.env.DATABASE_URL)
```

Every importer shares `pool`. No class, no `getInstance`, no private
constructor. If you have written a Singleton class in JavaScript, you have
reimplemented the module loader.

## Why the obvious version is still wrong
That snippet has a bug, and it has nothing to do with uniqueness:
`createPool` runs at **import time**.

- It runs before your config is loaded, if config loads in `main()`.
- It runs even when nothing ever touches `pool` — importing the module for one
  unrelated helper opens a database connection.
- It runs before a test can stub anything, because `import` is hoisted and
  evaluated before the importing module's own body.
- If it throws, it throws during module evaluation, where your error handling
  is not mounted yet and the stack points into the loader.

"One instance" and "created eagerly at import" got bundled together by
accident. Separate them:

```js
// db.js
let pool

export function getPool() {
  if (!pool) pool = createPool(config.databaseUrl)
  return pool
}
```

The module still guarantees one instance — `pool` is module-scoped and the
module is evaluated once — but creation happens on first use, after config
exists, inside a call you can stub and a stack you can read.

This is the JavaScript idiom: **a memoized factory in a module**, not a class.

## The failure mode nobody expects: two instances anyway
The module registry caches by *resolved specifier*, not by file contents. Two
specifiers that resolve differently produce two separate module instances, each
with its own `pool`. This is where real outages come from, because the symptom
is "my cache is empty about half the time" rather than an error.

Ways to end up with two copies of the same module:

- **Dual package hazard.** One importer does `require('./db')`, another does
  `import './db'`, and the package ships both CJS and ESM builds. Node loads
  both. Two registries, two pools.
- **A duplicated dependency.** On a version conflict npm hoists one copy to
  `node_modules/lib` and nests another at `node_modules/pkg/node_modules/lib`.
  `npm ls <lib>` shows you.
- **Specifiers that differ as strings.** `import('./db.js?v=2')` is a different
  key than `./db.js`. So is `./Db.js` on macOS, where the filesystem is
  case-insensitive but the registry key is not.
- **Server and client bundles.** A bundler builds two graphs. A module imported
  by both exists twice — which is correct, and is also why a module-level cache
  cannot be shared across that boundary.
- **Dev-server hot reload.** Every edit re-evaluates the module and builds a new
  `pool`, leaking the old one. Each save adds connections until the database
  starts refusing them.

That last one has a standard fix, and it is worth knowing because it is the one
case where bypassing the module registry is the right call:

```js
// Development: globalThis outlives the module registry across hot reloads.
const g = globalThis

export function getPool() {
  if (!g.__app_pool) g.__app_pool = createPool(config.databaseUrl)
  return g.__app_pool
}
```

Use it knowingly. `globalThis` is a shared namespace, so the key has to be
distinctive enough that another package doing the same thing does not collide
with yours.

## Tests
Module-level state lives as long as the module instance, which in most runners
means the whole file and sometimes the whole run. A memoized factory needs a
way out:

```js
export function resetPool() { pool = undefined }   // tests only
```

Vitest and Jest can instead drop the registry (`vi.resetModules()`,
`jest.resetModules()`), which re-evaluates the module and yields a fresh
`pool`. Either approach works. What does not work is hoping: a test that passes
alone and fails in the suite is almost always this.

The deeper fix is to need neither. A function that takes the pool as an
argument requires no reset, no module mocking, and no ordering. Keep the shared
instance at the edge of the program and pass it inward.

## What does not belong in JavaScript
- **A class with a private constructor and `getInstance()`.** The module already
  does this. The class adds a second mechanism and a second way to get it wrong.
- **`new.target` guards, or a constructor that returns an existing object.**
  `new Foo()` quietly handing back something it did not construct violates what
  `new` means, and every reader will misread it.
- **A `Symbol`-keyed global registry** — unless you are a library that genuinely
  must deduplicate across multiple copies of itself. Some libraries have that
  problem for real reasons. Application code almost never does.

## Watchouts
- `export const x = {}` gives one object, but the binding is live: reassigning
  it inside the owning module changes it for every importer. That is action at
  a distance.
- `Object.freeze` makes the object immutable, not the binding. It is a different
  guarantee than "only one".
- In a serverless runtime, module-level state survives between invocations on a
  warm instance and vanishes on a cold one. That is a cache with an
  unpredictable lifetime, not storage.
- Top-level `await` makes every importer wait on it. Combined with eager
  initialisation, one slow connection delays unrelated code paths.

## Thinking Style (transferable pattern)
In JavaScript the question is almost never "how do I get one instance" — the
module system answered that before you started. The questions that decide
whether it works are **when** it gets created, **what the second caller sees
when creation fails**, and **whether the module you believe is cached is really
loaded only once**. Two of those three are invisible until production.

## Practice
Take a module that does `export const client = createClient(...)` at the top
level. Convert it to a memoized factory, add a reset hook, and write two tests
that both pass whichever order they run in. Then run `npm ls` on the package it
wraps and confirm there is exactly one copy in the tree.
