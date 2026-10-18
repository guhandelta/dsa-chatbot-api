---
track: design-patterns
difficulty: Easy
patterns: adapter
category: Structural
source: generated-gap-fill
io_mode: function
review_status: source_linked_not_expert_certified
generated_on: 2026-10-18
---
# Adapter — Easy — Structural

## Problem
Existing code expects one interface, and a useful class or library provides a different one. Changing either side is not possible or not desirable.

## When to reach for it
Integrating a third-party library, a legacy module or a different data format behind the interface the rest of the code already uses. A wrapper translates calls and data in one place, so the rest of the code never sees the foreign API.

## When NOT to
If you own both sides and they are simple, change one of them. An adapter around an interface you control is extra indirection.

## Language notes
- **Any language** — a small wrapper class or a function that converts arguments and results.
- **Python / JavaScript** — duck typing means an adapter only needs the methods actually called.
- **Java / C#** — implement the expected interface and delegate to the wrapped object.
- **Go** — implicit interfaces make adapters short; a function type with a method (like `http.HandlerFunc`) adapts a function to an interface.
- **Rust** — a newtype wrapper implementing the needed trait; also the way around the orphan rule.
- **C++ / C** — wrapper classes, or a struct of function pointers in C.

## Watchouts
- Adapters that also add behaviour become decorators or facades; keep the purpose clear.
- Translate errors as well as data, or foreign exception types leak through the adapter.
- Two-way adapters are a sign the boundary is in the wrong place.
