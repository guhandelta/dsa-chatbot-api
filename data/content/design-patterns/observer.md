---
track: design-patterns
difficulty: Medium
patterns: observer
category: Behavioural
source: generated-gap-fill
io_mode: function
review_status: source_linked_not_expert_certified
generated_on: 2026-10-18
---
# Observer — Medium — Behavioural

## Problem
Several parts of a program need to react when something changes, and the thing that changes should not need to know who is listening.

## When to reach for it
Events in user interfaces, domain events ("order placed"), model-view updates and plugin hooks. Subscribers register a callback; the subject notifies all of them when its state changes.

## When NOT to
When there is exactly one consumer, a direct call is clearer. Event chains where one notification triggers others make control flow hard to follow and test.

## Language notes
- **JavaScript** — `addEventListener`/`EventTarget`, Node.js `EventEmitter`, signals in UI frameworks.
- **Python** — a list of callables; libraries such as blinker.
- **Java / C#** — listener interfaces; C# `event` and delegates; reactive libraries (RxJava, Rx.NET) for streams of events.
- **Go** — channels, or a slice of callback functions.
- **Rust** — channels (`std::sync::mpsc`, `tokio::sync::broadcast`) or callback vectors of boxed closures.
- **C++ / C** — vectors of `std::function`, or function pointers with a context pointer in C.

## Watchouts
- Unsubscribe, or listeners keep objects alive (memory leaks) and receive events after they should have stopped. `AbortSignal` with `addEventListener` and weak references are common remedies.
- Notification order between subscribers is usually unspecified; do not rely on it.
- Decide whether callbacks run synchronously or later, and what happens if one throws.
