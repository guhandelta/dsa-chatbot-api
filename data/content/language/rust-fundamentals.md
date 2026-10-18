---
track: language
difficulty: Easy
language: rust
category: Fundamentals
source: authored
io_mode: function
---
# Rust fundamentals — Easy — Fundamentals

- **Paradigm and typing:** multi-paradigm with traits instead of inheritance; static, strong typing with inference; generics are monomorphised; `Option<T>` replaces null.
- **Execution and memory:** compiled to native code; no garbage collector. Ownership rules: each value has one owner, dropped when the owner leaves scope; borrowing allows many `&T` or one `&mut T` at a time, checked at compile time. `Box<T>` for heap allocation, `Rc<RefCell<T>>` for shared mutable ownership.
- **Integers and overflow:** explicit widths (`i32`, `i64`, `u64`, `usize` for indices); Runtime integer overflow panics when overflow checks are enabled and wraps when they are disabled. Cargo defaults enable checks in dev and disable them in release, but profiles can override this. Use `checked_add`, `wrapping_add`, `saturating_add` to choose. No implicit numeric conversions; cast with `as`.
- **Division and modulo:** integer `/` truncates toward zero; `%` takes the sign of the dividend; `rem_euclid` gives a non-negative result.
- **Strings:** `String` (owned) and `&str` (borrowed), always valid UTF-8; `s[i]` is not allowed, so use `s.as_bytes()[i]` for ASCII or `s.chars()` for characters.
- **Equality:** `==` via the `PartialEq` trait; `#[derive(PartialEq, Eq, Hash, PartialOrd, Ord)]` generates comparisons. `f64` is only `PartialOrd`, so floats need `total_cmp` to sort.
- **Functions and recursion:** closures (`|x| x + 1`) implement `Fn`, `FnMut` or `FnOnce`; iterators are lazy and zero-cost. Main-thread stack size is determined outside Rust. Spawned-thread defaults depend on the platform and can change; configure supported spawned threads with `std::thread::Builder::stack_size` rather than assuming a portable depth.
- **Error handling:** `Result<T, E>` with the `?` operator; `panic!` for unrecoverable bugs.
- **Iteration idioms:** `for x in &v`, `iter().enumerate()`, `zip`, `map` / `filter` / `collect`, `windows(k)`, `chunks(k)`, `rev()`.
- **DSA pitfalls:** two mutable references into one `Vec` are rejected, so use indices or `split_at_mut`; subtracting below zero on `usize` follows the configured overflow checks; use `checked_sub` when underflow must be handled explicitly; `HashMap` iteration order is random per run (use `BTreeMap` for deterministic output); trees and graphs with back-pointers are easiest as index-based arenas (`Vec<Node>` with `usize` ids).

Correction sources reviewed October 17, 2026 (scope: the qualifications above):

- https://doc.rust-lang.org/cargo/reference/profiles.html#overflow-checks
- https://doc.rust-lang.org/std/thread/index.html#stack-size
