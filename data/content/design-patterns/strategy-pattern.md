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
where each branch is self-contained and callers need to choose among them.
Extracting the alternatives behind a common contract can let callers add or
select behaviour without editing the central conditional.

## When NOT to
When the alternatives are few, stable, and used in one place, a conditional
may be clearer. The number of cases alone does not decide whether Strategy is
useful; independent variation, testing needs, and ownership of the choice
matter more. Adding layers before those needs exist can make the code harder
to follow.

## Language notes
Most languages express this without the class ceremony the original form
describes:

- **Python / JavaScript** — pass a function. That *is* the strategy.
- **Rust** — a trait object, or a generic bound for static dispatch.
- **Java / C#** — a functional interface, or a lambda.
- **C++** — `std::function`, or a template parameter.
- **C** — a function pointer in a struct.

## Watchouts
- Strategy and State can have similar interfaces. The difference is intent:
  Strategy selects among interchangeable behaviours; State models behaviour
  associated with an object's changing state.
- Passing a strategy *and* a flag that selects it defeats the purpose.
- Stateless strategies can be shared; stateful ones must not be.

## Thinking Style (transferable pattern)
Ask who decides which algorithm runs, and when. "The caller, at call time" is
Strategy. "The object, based on what just happened" is State.
