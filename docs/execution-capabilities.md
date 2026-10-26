# Execution capabilities

The API reports the active environment at `GET /tracks/capabilities` for the
learner's permitted languages and at `GET /training/status` for instructors.
Use `PYTHONPATH=. .venv/bin/python tools/audit_execution_capabilities.py` to
inspect the same registry locally. `installed` means the configured execution
backend passed its toolchain probe. It does not certify a particular student
program; only executed test cases can do that.

Function-style test adapters currently cover Python, JavaScript, TypeScript,
Java, C, C++, Rust, Ruby, Go and C#. Stdin/stdout adapters cover those languages
except C#, plus PHP, Dart, Kotlin, Swift, Scala and Haskell. A missing toolchain
or unsupported test mode reports `unverified` and blocks publication. The
bundled Dockerfile does not yet provide all six additional toolchains; their
stdin/stdout adapters become usable only in an operator-provided image with
those runtimes installed and a pinned image digest. Browser, server, mobile and
circuit previews are not claimed by this registry.

All learner execution uses `code_runner._run`. Production requires the Docker
backend. It runs with a pinned image, no network, a read-only root, dropped
capabilities, no privilege escalation, process and memory limits, a wall-clock
timeout, bounded output, and a disposable mounted scratch directory. Only
trusted test environments may opt into the host subprocess backend; process
limits there do not isolate the host filesystem or network. Each stdin/stdout
submission accepts at most 64 cases, 100 KB of source, and 64 KB per input.
The application should hide unavailable run controls using the capability API.

The adapter source filename is the expected entry point. Java and Scala use a
`Main` class, Kotlin uses a runnable `main`, Go uses `package main`, and the
other languages use their normal executable entry point. Framework projects,
dependencies, browser previews and multi-file sessions need separate adapters
in a later phase.
