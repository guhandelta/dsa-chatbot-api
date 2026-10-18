---
track: design-patterns
difficulty: Easy
patterns: factory
category: Creational
source: generated-gap-fill
io_mode: function
review_status: source_linked_not_expert_certified
generated_on: 2026-10-18
---
# Factory — Easy — Creational

## Problem
Code needs to create objects whose exact class depends on input or configuration, and the calling code should not have to know every concrete class.

## When to reach for it
A `switch` on a type string repeated in several places, each one constructing a different class. Centralizing creation in one function or factory object puts the knowledge of concrete classes in one place, and callers depend on the shared interface only. Parsers that build different node types and plugins selected by name are common cases.

## When NOT to
If there is one concrete class, or the caller always knows which class it wants, call the constructor. A factory per class with nothing to decide is ceremony.

## Language notes
- **Python / JavaScript / Ruby** — a plain function or a dict/map from key to class or constructor is usually enough; classes are values.
- **Java / C#** — a static factory method (`List.of`, `Path.of`) or an interface with implementations; enum-keyed maps of `Supplier`/`Func`.
- **Go** — `NewThing(...)` constructor functions returning an interface or concrete type are the idiom.
- **Rust** — associated functions (`Thing::new`, `Thing::from_config`) returning `Box<dyn Trait>` or an enum; enums often replace class hierarchies entirely.
- **C++** — functions returning `std::unique_ptr<Base>`.
- **C** — a function returning a pointer to a struct with function pointers, or a tagged union.

## Watchouts
- "Factory Method" in the original catalogue means a subclass overrides a creation method; most modern uses are simple factories. Be clear which one you mean.
- A factory that grows a branch for every new type has only moved the `switch`; a registry (map from key to constructor) lets new types register themselves.
- Return the interface type, or callers will start depending on concrete classes again.
