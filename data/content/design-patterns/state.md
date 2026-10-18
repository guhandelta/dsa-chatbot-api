---
track: design-patterns
difficulty: Medium
patterns: state
category: Behavioural
source: generated-gap-fill
io_mode: function
review_status: source_linked_not_expert_certified
generated_on: 2026-10-18
---
# State — Medium — Behavioural

## Problem
An object's behaviour depends on which state it is in, and conditionals on a state variable are spreading through many methods.

## When to reach for it
Workflows with explicit states (draft, submitted, approved), connection lifecycles, parsers and game entities. Each state handles events and decides the next state, keeping state-specific logic together and transitions explicit.

## When NOT to
With two or three states and few transitions, an enum and a `switch` are clearer than one class per state.

## Language notes
- **Rust / TypeScript / Kotlin** — an enum or discriminated union of states with a `match`; Rust's typestate pattern encodes states in types so invalid transitions do not compile.
- **Java / C#** — sealed interfaces or classes with pattern matching (Java 21, C# 9+), or classic state objects.
- **Python / JavaScript** — a dict from state to handler, or the `match` statement in Python 3.10+.
- **C / Go** — an enum plus a transition table, which is also easy to test exhaustively.

## Watchouts
- State and Strategy are structurally identical; the difference is that states choose their successors.
- Write down the transition table; untested transitions are where bugs live.
- Persisted state needs a migration plan when states are added or renamed.
