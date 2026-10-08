---
track: design-patterns
difficulty: Medium
patterns: strategy
category: Behavioural
source: authored
io_mode: function
---
# Strategy — Medium — Behavioural

## Problem
Several interchangeable algorithms do the same job, and the choice belongs to
the caller rather than being baked into the code that runs them.

## When to reach for it
A conditional that keeps growing — `if mode == "a" ... elif mode == "b"` —
where each branch is self-contained. Extracting each branch behind a common
interface turns "add a case" into "add a file" instead of "edit a switch".

## When NOT to
With two cases that will only ever be two, a conditional is clearer than three
new types. Strategy pays off at the third case, not the first. Applied early it
is over-engineering, and recognising that is as much the skill as knowing the
pattern.

## Language notes
Most languages express this without the class ceremony the original form
describes:

- **Python / JavaScript** — pass a function. That *is* the strategy.
- **Rust** — a trait object, or a generic bound for static dispatch.
- **Java / C#** — a functional interface, or a lambda.
- **C++** — `std::function`, or a template parameter.
- **C** — a function pointer in a struct.

## Watchouts
- Strategy and State are structurally identical. The difference is intent:
  Strategy is chosen by the caller, State transitions itself.
- Passing a strategy *and* a flag that selects it defeats the purpose.
- Stateless strategies can be shared; stateful ones must not be.

## Thinking Style (transferable pattern)
Ask who decides which algorithm runs, and when. "The caller, at call time" is
Strategy. "The object, based on what just happened" is State.
