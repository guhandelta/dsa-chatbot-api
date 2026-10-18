---
track: design-patterns
difficulty: Easy
patterns: facade
category: Structural
source: generated-gap-fill
io_mode: function
review_status: source_linked_not_expert_certified
generated_on: 2026-10-18
---
# Facade — Easy — Structural

## Problem
Using a subsystem requires many steps across several classes, and most callers only need a few common operations.

## When to reach for it
Callers repeat the same sequence of setup calls (create client, configure, authenticate, build request, parse response). A facade offers a small, task-shaped API (`fetch_user(id)`) and hides the sequence, while the full subsystem stays available for advanced use.

## When NOT to
When callers genuinely need the subsystem's flexibility, a facade that exposes every option has become a second copy of the subsystem.

## Language notes
- **All languages** — a module or class with a few high-level functions. In Python and JavaScript, a module itself is often the facade.
- **Java / C# / Go / Rust** — a service type that holds the subsystem objects and exposes task-level methods.

## Watchouts
- A facade that grows to cover everything turns into a "god object". Keep it focused on common tasks.
- Facades are a good place for an adapter boundary to external services, but do not hide errors the caller must handle.
