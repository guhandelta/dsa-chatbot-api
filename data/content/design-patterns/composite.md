---
track: design-patterns
difficulty: Medium
patterns: composite
category: Structural
source: generated-gap-fill
io_mode: function
review_status: source_linked_not_expert_certified
generated_on: 2026-10-18
---
# Composite — Medium — Structural

## Problem
A structure is a tree of parts and wholes (files and folders, UI widgets, expression trees, organization charts), and code should treat a single item and a group the same way.

## When to reach for it
Operations such as "total size", "render" or "evaluate" that recurse over a tree. Giving leaves and containers a common interface lets the operation be written once, with containers delegating to their children.

## When NOT to
If the tree has a fixed shape or only one kind of node, a plain recursive data structure is clearer. Forcing leaf-only operations (like "add child") onto every node creates methods that must throw.

## Language notes
- **Rust / TypeScript / functional styles** — an enum or discriminated union (`Leaf | Node(children)`) with a recursive function over it is often clearer than a class hierarchy.
- **Java / C# / C++** — an interface or abstract base implemented by leaf and container classes; containers hold a list of the interface type.
- **Python / Ruby / JavaScript** — duck-typed objects with the same method, or nested dicts and lists with a recursive function.
- **Go** — an interface with a method; containers hold a slice of the interface.

## Watchouts
- Deep trees and recursive operations have recursion depth limits; very deep structures may need an explicit stack.
- Cycles turn a tree into a graph; recursive operations then need a visited set.
- Decide whether parent links are needed; they complicate ownership in Rust and C++.
