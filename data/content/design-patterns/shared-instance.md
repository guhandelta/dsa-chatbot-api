---
track: design-patterns
difficulty: Easy
patterns: singleton
category: Creational
source: authored
io_mode: function
---
# One Shared Instance — Easy — Creational

## Problem
Something must exist exactly once in a process — a database pool, a config
object, a logger, a cache — and every caller must reach that same one rather
than a copy of it.

## When to reach for it
The need is real when a second copy would be *wrong*, not merely wasteful:

- two connection pools open twice the connections the database allows
- two caches disagree, and which one you read is luck
- two config objects mean a setting changed at runtime takes effect in half
  the application

If a second copy would only waste memory, this is not this problem. That is a
caching question, and it has different answers.

## When NOT to
"One instance" is the easiest requirement to over-apply, because declaring it
costs nothing and the bill arrives later:

- **It is global mutable state.** Every test that touches it inherits whatever
  the previous test left behind. This is the most common single reason a suite
  passes test-by-test and fails as a run.
- **It hides dependencies.** A function that reaches for the shared instance
  does not name it in its signature, so you cannot tell what a module needs by
  reading its interface.
- **One per process is not one per deployment.** Run two processes and you have
  two instances. If the invariant you actually need is "one across the system",
  this pattern gives you nothing and the answer is a lock or a database row.

Passing the thing as an argument costs one parameter and buys back
testability. Reach for a shared instance when threading it through is
genuinely impractical, not when it is merely tedious.

## Where this is a real pattern

| Language | Status | What you write |
|---|---|---|
| Java | real pattern | an `enum` singleton, or a static holder class |
| C++ | real pattern | a function-local `static` (thread-safe since C++11) |
| C# | real pattern | `static readonly`, or `Lazy<T>` |
| Python | mostly free | modules are cached in `sys.modules` — a module-level name is already one |
| JavaScript | mostly free | the module registry caches the module — an export is already one |
| Rust | a different problem | `OnceLock` / `LazyLock`; the compiler makes you confront sharing |
| C | manual | a file-scope `static` plus an init guard you write yourself |

The split in that table is the lesson. In Java and C++ you build the mechanism.
In Python and JavaScript the module system already built it, and a Singleton
class layered on top is ceremony that adds a second way to get it wrong. In
Rust the borrow checker refuses to let you pretend shared mutable state is
simple, so the pattern becomes an explicit decision about synchronisation.

## Watchouts
- Lazy initialisation and "one instance" are separate decisions. Bundling them
  is how you end up with a first call that is slow, fallible, and on the wrong
  thread.
- Initialisation that can fail needs an answer to "what does the second caller
  get after the first one threw". Caching the failure and retrying are both
  defensible; having no answer is not.
- A "reset for tests" hook is an admission that the thing is global. Add it
  anyway — the alternative is tests that cannot isolate.

## Thinking Style (transferable pattern)
Ask two questions, in order. First: *would a second copy be incorrect, or just
wasteful?* Only "incorrect" justifies the pattern. Second: *does my language
already give me one?* If the module system or the type system hands it to you,
take it and write nothing.
