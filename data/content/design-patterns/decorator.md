---
track: design-patterns
difficulty: Medium
patterns: decorator
category: Structural
source: generated-gap-fill
io_mode: function
review_status: source_linked_not_expert_certified
generated_on: 2026-10-18
---
# Decorator — Medium — Structural

## Problem
Behaviour such as logging, caching, retrying, timing or access checks needs to be added around existing operations without changing their code, and different combinations are needed in different places.

## When to reach for it
Cross-cutting concerns that would otherwise be copied into many methods. A decorator implements the same interface as the wrapped object, does its extra work, and delegates. Decorators stack: a cached, retrying, logged client.

## When NOT to
If only one combination is ever used, putting the behaviour directly in the class is simpler. Deep stacks of decorators make stack traces and debugging harder.

## Language notes
- **Python** — function decorators (`@functools.lru_cache`, `@functools.wraps` to keep metadata) are this pattern for functions. Class-level wrappers for objects.
- **JavaScript / TypeScript** — higher-order functions; TypeScript 5.0 supports standard ECMAScript decorators, distinct from the older `experimentalDecorators`.
- **Java / C#** — wrapper classes implementing the same interface (`BufferedReader` wraps a `Reader`); frameworks often use proxies for the same effect.
- **Go** — middleware functions `func(http.Handler) http.Handler`.
- **Rust** — wrapper structs generic over the inner type implementing the same trait (as in `tower` layers).
- **C++** — wrapper classes or templates; **C** — wrapper functions with the same signature.

## Watchouts
- Python's `@decorator` syntax is a language feature that can implement this pattern, but is not limited to it.
- Order matters: caching outside retry behaves differently from retry outside caching.
- A decorator that changes the interface is an adapter.
