---
track: design-patterns
difficulty: Easy
patterns: builder
category: Creational
source: generated-gap-fill
io_mode: function
review_status: source_linked_not_expert_certified
generated_on: 2026-10-18
---
# Builder — Easy — Creational

## Problem
An object has many optional parameters or must be assembled in steps, and a constructor with a long argument list is hard to read and easy to call wrongly.

## When to reach for it
Constructors with several parameters of the same type (`new Query(10, 20, true, false)`), many overloads, or objects that must be validated as a whole before use. A builder names each setting and validates once in `build()`.

## When NOT to
Languages with named and default arguments (Python, Kotlin, C#, Ruby keyword arguments, JavaScript option objects) already solve readability; a builder there adds code without benefit unless construction really happens in stages.

## Language notes
- **Python** — keyword arguments with defaults, or a dataclass; `dataclasses.replace` for modified copies.
- **JavaScript / TypeScript** — an options object with defaults (`{ limit = 10, sort = "asc" } = {}`).
- **Java** — the builder pattern is common (Lombok `@Builder`, `HttpRequest.newBuilder()`); records with compact constructors for validation.
- **C#** — object initializers and `init` properties; `with` expressions for records.
- **Rust** — builder structs with methods taking and returning `self` are idiomatic (for example `std::process::Command`); `Default` plus struct update syntax for simple cases.
- **Go** — functional options (`NewServer(WithPort(8080), WithTLS(cfg))`) or a config struct.
- **C++** — designated initializers (C++20) for aggregates, or a builder class.

## Watchouts
- A builder that allows `build()` before required fields are set just moves the error to run time; validate in `build()` or use types to require them (typestate builders in Rust and TypeScript).
- Mutable builders reused after `build()` can leak state into the next object.
- Don't confuse with the step-by-step "director" variant from the original catalogue; it is rarely needed.
