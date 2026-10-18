---
track: design-patterns
difficulty: Medium
patterns: command
category: Behavioural
source: generated-gap-fill
io_mode: function
review_status: source_linked_not_expert_certified
generated_on: 2026-10-18
---
# Command — Medium — Behavioural

## Problem
Requests need to be treated as data: queued, logged, retried, undone, or executed later or elsewhere.

## When to reach for it
Undo/redo stacks in editors, job queues, macro recording, and transactional operations. Each command object carries what is needed to execute (and possibly undo) one action.

## When NOT to
When an action only ever runs immediately and once, a direct method call or a plain function is enough.

## Language notes
- **Python / JavaScript / Ruby** — a function or closure is a command; a dataclass or plain object when it must be serialized or undone.
- **Java / C#** — `Runnable`, `Callable`, `Func`/`Action`, or a command interface with `execute`/`undo`.
- **Rust** — an enum of command variants with a `match` in the executor is idiomatic and serializable; boxed closures when variants are open-ended.
- **Go** — function values, or structs implementing an interface.

## Watchouts
- Undo requires each command to capture enough state to reverse itself; for some operations storing a snapshot is simpler.
- Serialized commands (for queues) need versioning when their shape changes.
- Retried commands must be idempotent or detect duplicates.
