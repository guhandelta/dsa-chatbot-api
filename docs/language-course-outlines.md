# Language course outlines — DRAFT

Offline audit and authored draft, 2026-10-19. These outlines are not a validated full curriculum. All 12 courses have missing reviewed assessments. No network, LLM, source execution or external citation verification was used.

## Public service contract

`app.services.course_catalog` exposes synchronous `list_courses()`, `get_course(language)` and `get_lesson(language, module_id, source_id)`. Unknown languages, modules, unassigned sources and currently ineligible lessons return `None`.

- List: `language`, `title`, `description`, `status`, `assessment_status`, `module_count`, `source_count`.
- Course: `id`, `language`, `title`, `description`, `status: draft`, `assessment_status: missing`, `prerequisites: string[]`, `modules`, `capstone`, `coverage`, `limitations`.
- Module: `id`, `title`, `objectives: string[]`, `practice_brief: string`, `prerequisites: string[]` (earlier module IDs), `sources`, `source_status: available | partial | missing`. Array order is teaching order.
- Source: `id`, `title`, `kind`, `collection: reference_library | curriculum | content_catalog`, `origin`. IDs use existing reference IDs, `corpus-` plus curriculum row ID, or a pinned content-catalog ID.
- Capstone: `title`, `brief`, `deliverables: string[]`, `assessment_status: missing`. Deliverables are proposed work, not a reviewed scoring rubric.
- Coverage: `reference_rows`, `curriculum_rows` (audit snapshot counts), `selected_sources` (currently available assigned readings, including repeated assignments), and optional `foundational_status`.
- Lesson: `language`, `module_id`, `source_id`, `title`, `document`, `metadata`, `status: draft`. No payload, grader or private exercise answers are returned.

Aliases: `c++ → cpp`, `c#/cs → csharp`, `js → javascript`, `ts → typescript`, `py → python`, `golang → go`, `html5 → html`, `css3/scss/sass → css`. Whitespace and case are normalized. Sass/SCSS remains a preprocessor collection associated with CSS; it is not a thirteenth course. Framework and embedded subject IDs do not resolve as courses.

## Audit and eligibility

The audit read all 15,265 local `data/reference_library/records.jsonl` rows and all 4,280 `data/curriculum/java-javascript.jsonl` rows. Among the 12 language subjects, 6,477 reference rows and 2,613 Java/JavaScript curriculum rows pass the shared current eligibility policy. Counts describe eligible readings, not lesson counts or validated coverage. Framework and embedded rows are counted separately below.

Reference/curriculum eligibility requires explicit `contains_answer: false`, kind `concept` or `reference`, nonempty text and no current quarantine reason. Authoring plans, curriculum-outline rows, exercise/gotcha answers, mixed quarantined extracts and the known unsafe C graph row are excluded. A matching language alone is insufficient: reference subject must equal the course language.

The modules are authored around exact selected source content, not runtime keyword matching. The plan initially selected 65 concise language-specific reference readings, then added 22 pinned catalog foundation readings and two eligible curriculum readings. Catalog readings are explicit language-track items, projected through `content_access.public_text` to remove front matter and protected sections. Catalog reference prose can include illustrative examples; missing assessment does not mean every explanatory code example is hidden. Local learner-safe eligibility is not independent factual certification.

Each lesson rechecks current eligibility and exact module membership. Course detail omits unavailable sources and changes module source_status to partial or missing, including when no sources are assigned. Versioned source indexes follow corpus file changes. Course JSON is read afresh. Coverage inventory counts remain the dated audit snapshot; selected_sources reflects current resolution. No arbitrary path supplied by the caller is opened.

## Course inventory

12 courses, 75 modules, 89 reading assignments (89 distinct source IDs). All draft; all assessments missing.

| Language | Modules | Eligible reference rows | Eligible curriculum rows | Selected readings |
| --- | ---: | ---: | ---: | ---: |
| c | 6 | 796 | 0 | 6 |
| cpp | 6 | 341 | 0 | 6 |
| csharp | 7 | 25 | 0 | 7 |
| go | 7 | 28 | 0 | 7 |
| java | 7 | 26 | 1498 | 12 |
| javascript | 7 | 26 | 1115 | 12 |
| python | 7 | 434 | 0 | 11 |
| ruby | 6 | 827 | 0 | 6 |
| rust | 7 | 1629 | 0 | 7 |
| typescript | 7 | 1290 | 0 | 7 |
| html | 4 | 255 | 0 | 4 |
| css | 4 | 800 | 0 | 4 |

## Separate subject collections

| Subject | Language association | Classification | Eligible rows |
| --- | --- | --- | ---: |
| bootstrap | css | framework_or_preprocessor | 95 |
| bulma | css | framework_or_preprocessor | 42 |
| embedded-c | c | embedded | 1448 |
| embedded-python | python | embedded | 829 |
| python-django | python | framework_or_preprocessor | 321 |
| python-fastapi | python | framework_or_preprocessor | 320 |
| python-flask | python | framework_or_preprocessor | 320 |
| sass | css | framework_or_preprocessor | 35 |
| shadcn | css | framework_or_preprocessor | 73 |
| spring-boot | java | framework_or_preprocessor | 6 |
| spring-core | java | framework_or_preprocessor | 4 |
| spring-data | java | framework_or_preprocessor | 5 |
| spring-mvc | java | framework_or_preprocessor | 6 |
| spring-security | java | framework_or_preprocessor | 4 |
| spring-testing | java | framework_or_preprocessor | 4 |
| tailwind | css | framework_or_preprocessor | 48 |

## Scope and gaps

Programming courses begin with a `language-00` foundations module, and `language-01` depends on it. Java, JavaScript and Python include dedicated values, conditions, loops and functions pages. The other seven programming languages currently have compact overview readings: prior programming literacy is recommended, and step-by-step syntax practice remains missing. TypeScript explicitly requires JavaScript basics. HTML begins with parsed structure; CSS requires basic HTML and begins with cascade and values. These are honest starting requirements rather than a claim of complete zero-to-expert instruction.

Advanced modules intentionally differ: C emphasizes bounds, allocation and atomic mutation; C++ emphasizes RAII, moves and generic contracts; Go emphasizes shared slices and goroutine ownership; Ruby emphasizes callable control flow and mutable state; Rust emphasizes borrowing and unsafe boundaries; HTML/CSS emphasize native semantics, forms, cascade, layout and browser evidence. Shared foundations are used only where relevant.

All modules have proposed practice briefs, but there is no reviewed question bank, answer key, rubric, mastery threshold, duration estimate or course-completion certification. Capstones are proposed projects and carry the same missing-assessment label. Java/JavaScript executable release material elsewhere does not promote these new outlines to validated status. Large eligible inventories do not establish that every beginner topic or standard-library API has been taught.

## Ordered teaching plans

### C: source-backed draft course

Prerequisites: Ability to edit text and run a local program; begin with the foundations module. Prior programming literacy is recommended for the compact overview.

- **c-00 — C foundations: values, functions and iteration**. Objectives: Identify how C represents values, strings, equality and function calls. Trace the reference’s iteration idiom and explain its mutation or ownership behavior. Practice: Use the C overview to annotate a short sequence-processing function: input types, iteration, equality and failure path. Record syntax you still need to learn before proceeding. Readings: `c-fundamentals` (content_catalog; C fundamentals).
- **c-01 — Translation units and storage**. Objectives: Explain separate compilation and distinguish object storage durations. Practice: Split a tiny program into a header and two translation units; annotate the lifetime of every shared object. Readings: `ref-gapfill-v1-c-translation-units-headers-and-storage-duration` (reference_library; Translation units headers and storage duration).
- **c-02 — Bounds and representation**. Objectives: Identify valid pointer ranges and reserve space for string termination. Practice: Design a bounded string-copy interface and enumerate empty, full and unterminated input cases. Readings: `ref-gapfill-v1-c-pointer-bounds-strings-and-integer-conversions` (reference_library; Pointer bounds strings and integer conversions).
- **c-03 — Allocation and ownership**. Objectives: Check allocation-size arithmetic and assign one cleanup owner per allocation. Practice: Draft a growable buffer contract with allocation-failure and partial-initialization paths. Readings: `ref-gapfill-v1-c-allocation-size-overflow-and-cleanup-ownership` (reference_library; Allocation size overflow and cleanup ownership).
- **c-04 — Failure reporting**. Objectives: Interpret failure sentinels before reading errno or stream state. Practice: Write a file-reading interface brief that distinguishes end of file, read failure and caller misuse. Readings: `ref-gapfill-v1-c-error-return-contracts-errno-and-stream-state` (reference_library; Error return contracts errno and stream state).
- **c-05 — Atomic graph mutation**. Objectives: Preserve symmetric adjacency when either allocation fails. Practice: Trace both allocation failures during edge insertion and document the unchanged-state guarantee. Readings: `ref-gapfill-v1-c-atomic-undirected-adjacency-insertion-on-allocation-failure` (reference_library; Atomic undirected adjacency insertion on allocation failure).

Capstone: **A failure-safe adjacency-list library**. Build a small graph library with explicit allocation ownership and atomic edge insertion. Assessment: missing.

### C++: source-backed draft course

Prerequisites: Ability to edit text and run a local program; begin with the foundations module. Prior programming literacy is recommended for the compact overview.

- **cpp-00 — C++ foundations: values, functions and iteration**. Objectives: Identify how C++ represents values, strings, equality and function calls. Trace the reference’s iteration idiom and explain its mutation or ownership behavior. Practice: Use the C++ overview to annotate a short sequence-processing function: input types, iteration, equality and failure path. Record syntax you still need to learn before proceeding. Readings: `cpp-fundamentals` (content_catalog; C++ fundamentals).
- **cpp-01 — Declarations and initialization**. Objectives: Distinguish overload selection, initialization forms and value categories. Practice: Compare brace and parenthesis initialization for a small class and explain the selected constructors. Readings: `ref-gapfill-v1-cpp-declarations-overloads-value-categories-and-initialization` (reference_library; Declarations overloads value categories and initialization).
- **cpp-02 — RAII and borrowed views**. Objectives: Separate owner lifetime from the lifetime of a span or string_view. Practice: Design an owning text store and a view API; identify which operations invalidate each view. Readings: `ref-gapfill-v1-cpp-object-lifetime-raii-references-and-views` (reference_library; Object lifetime RAII references and views).
- **cpp-03 — Moves and failure guarantees**. Objectives: Explain what std::move permits and state a compound operation’s exception guarantee. Practice: Specify a collection update under throwing element construction and track valid moved-from objects. Readings: `ref-gapfill-v1-cpp-moves-copies-and-exception-guarantees` (reference_library; Moves copies and exception guarantees).
- **cpp-04 — Containers and ordering**. Objectives: Apply iterator invalidation rules and strict weak ordering. Practice: Choose a container for an index and write comparator boundary cases without subtraction overflow. Readings: `ref-gapfill-v1-cpp-container-invalidation-comparator-contracts-and-complexity` (reference_library; Container invalidation comparator contracts and complexity).
- **cpp-05 — Generic APIs**. Objectives: Use constraints to express generic requirements and interpret deduction failures. Practice: Specify a constrained search helper and record examples that should and should not compile. Readings: `ref-gapfill-v1-cpp-templates-concepts-deduction-and-diagnostics` (reference_library; Templates concepts deduction and diagnostics).

Capstone: **An owning indexed collection**. Build an indexed collection whose views, mutation rules and exception guarantees are documented. Assessment: missing.

### C#: source-backed draft course

Prerequisites: Ability to edit text and run a local program; begin with the foundations module. Prior programming literacy is recommended for the compact overview.

- **csharp-00 — C# foundations: values, functions and iteration**. Objectives: Identify how C# represents values, strings, equality and function calls. Trace the reference’s iteration idiom and explain its mutation or ownership behavior. Practice: Use the C# overview to annotate a short sequence-processing function: input types, iteration, equality and failure path. Record syntax you still need to learn before proceeding. Readings: `csharp-fundamentals` (content_catalog; C# fundamentals).
- **csharp-01 — Projects and runtime boundaries**. Objectives: Distinguish SDK, target framework and language-version settings. Practice: Create a project checklist that records effective SDK, target framework and build inputs. Readings: `generated-csharp-project-sdk-v1` (reference_library; C# projects and the .NET SDK).
- **csharp-02 — Nullability and values**. Objectives: Separate nullable analysis from runtime boundary validation. Practice: Design an input API that permits optional fields and rejects required null values at runtime. Readings: `generated-csharp-nullable-reference-types-v1` (reference_library; C# nullable reference types: annotations and analysis).
- **csharp-03 — Collections and equality**. Objectives: Choose generic collection and comparer contracts for an indexed model. Practice: Specify duplicate-key handling and equality cases for a typed record index. Readings: `ref-gapfill-v1-csharp-generics-collections-comparers-and-pattern-matching` (reference_library; Generics collections comparers and pattern matching).
- **csharp-04 — LINQ execution**. Objectives: Explain deferred execution and the effects of repeated enumeration. Practice: Trace a query before and after source mutation; choose where materialization is required. Readings: `ref-gapfill-v1-csharp-linq-deferred-repeated-and-provider-execution` (reference_library; LINQ deferred repeated and provider execution).
- **csharp-05 — Resource lifetime**. Objectives: Assign disposal ownership and distinguish using from await using. Practice: Outline a reader pipeline with cleanup on success and exception and no use after disposal. Readings: `generated-csharp-disposal-v1` (reference_library; C# deterministic resource disposal).
- **csharp-06 — Async failure and cancellation**. Objectives: Observe task failures and propagate cooperative cancellation. Practice: Design cancellation and fault paths for the record tool without blocking on Result. Readings: `generated-csharp-async-await-v1` (reference_library; C# asynchronous methods with async and await).

Capstone: **A cancellable record-processing tool**. Process records with explicit null validation, collection semantics and deterministic disposal. Assessment: missing.

### Go: source-backed draft course

Prerequisites: Ability to edit text and run a local program; begin with the foundations module. Prior programming literacy is recommended for the compact overview.

- **go-00 — Go foundations: values, functions and iteration**. Objectives: Identify how Go represents values, strings, equality and function calls. Trace the reference’s iteration idiom and explain its mutation or ownership behavior. Practice: Use the Go overview to annotate a short sequence-processing function: input types, iteration, equality and failure path. Record syntax you still need to learn before proceeding. Readings: `go-fundamentals` (content_catalog; Go fundamentals).
- **go-01 — Modules and packages**. Objectives: Distinguish module identity, package imports and exported identifiers. Practice: Sketch a two-package module and diagnose a mismatched import path from its go.mod. Readings: `generated-go-modules-packages-v1` (reference_library; Go modules, packages, and dependency versions).
- **go-02 — Slices and aliasing**. Objectives: Explain shared backing storage and use the slice returned by append. Practice: Trace overlapping slices and specify when the indexer must copy input storage. Readings: `generated-go-slices-sharing-v1` (reference_library; Go slices: length, capacity, and shared storage).
- **go-03 — Interfaces and errors**. Objectives: Explain typed-nil interfaces and preserve inspectable wrapped errors. Practice: Design a small consumer-side interface and error contract with errors.Is/As cases. Readings: `generated-go-interfaces-errors-v1` (reference_library; Go interfaces and error handling).
- **go-04 — Maps and absence**. Objectives: Distinguish missing keys from zero values and avoid iteration-order assumptions. Practice: Specify an index update operation with missing-key, duplicate-key and iteration cases. Readings: `ref-gapfill-v1-go-map-absence-mutation-and-iteration` (reference_library; Map absence mutation and iteration).
- **go-05 — Channels and ownership**. Objectives: Assign channel closure and goroutine lifecycle responsibility. Practice: Draw the indexer worker shutdown sequence and account for blocked senders and receivers. Readings: `ref-gapfill-v1-go-channels-select-closure-and-goroutine-ownership` (reference_library; Channels select closure and goroutine ownership).
- **go-06 — Cancellation and synchronization**. Objectives: Propagate cancellation and identify synchronization boundaries. Practice: Write a bounded worker plan with cancellation during input, processing and result delivery. Readings: `ref-gapfill-v1-go-context-cancellation-synchronization-and-memory-model` (reference_library; Context cancellation synchronization and memory model).

Capstone: **A bounded concurrent indexer**. Build a package-based indexer with explicit slice ownership, error contracts and worker shutdown. Assessment: missing.

### Java: source-backed draft course

Prerequisites: Ability to edit text and run a local program; begin with the foundations module. Prior programming literacy is recommended for the compact overview.

- **java-00 — Java foundations: values, functions and iteration**. Objectives: Identify how Java represents values, strings, equality and function calls. Trace the reference’s iteration idiom and explain its mutation or ownership behavior. Write a conditional, a terminating loop and a small function using the dedicated beginner readings. Practice: Use the Java overview to annotate a short sequence-processing function: input types, iteration, equality and failure path. Record syntax you still need to learn before proceeding. Readings: `java-fundamentals` (content_catalog; Java fundamentals); `java-path-01-values` (content_catalog; Java values); `java-path-02-conditions` (content_catalog; Java conditions); `java-path-03-loops` (content_catalog; Java loops); `java-path-04-functions` (content_catalog; Java functions).
- **java-01 — Packages and modules**. Objectives: Separate package access, module exports and reflective opens. Practice: Sketch two modules and diagnose why a public class is still inaccessible. Readings: `generated-java-modules-packages-v1` (reference_library; Java packages and modules: separate organization and access controls).
- **java-02 — Collections and equality**. Objectives: Keep equality, hashing and ordering contracts consistent. Explain the assigned array-mutation reading and trace its index/value or shifting behavior. Practice: Design a record key and list duplicate, mutable-key and comparator edge cases. Readings: `ref-gapfill-v1-java-equality-ordering-hashing-and-collection-complexity` (reference_library; Equality ordering hashing and collection complexity); `corpus-java-list-remove-index-vs-value` (curriculum; List<Integer>.remove(int) removes by index, remove(Object) by value).
- **java-03 — Generics and API variance**. Objectives: Explain invariant generic types and bounded producer/consumer APIs. Practice: Specify a collection-copy API and document accepted and rejected type relationships. Readings: `ref-gapfill-v1-java-generics-invariance-and-bounded-wildcards` (reference_library; Generics invariance and bounded wildcards).
- **java-04 — Cleanup and exceptions**. Objectives: Explain reverse close order and primary versus suppressed failures. Practice: Trace two resources when processing and close both fail; document ownership. Readings: `generated-java-resource-lifetime-v1` (reference_library; Java resource lifetime and try-with-resources).
- **java-05 — Stream pipelines**. Objectives: Distinguish lazy intermediate operations from terminal consumption. Practice: Design a reduction without shared mutation and identify why stream reuse is invalid. Readings: `generated-java-streams-v1` (reference_library; Java Stream API: lazy pipelines and safe behavior).
- **java-06 — Executor lifecycle**. Objectives: Observe task failures and assign executor shutdown responsibility. Practice: Plan bounded batch submission with interruption and shutdown paths. Readings: `generated-java-concurrency-executor-v1` (reference_library; Java concurrency: tasks, executors, and lifecycle).

Capstone: **A resource-safe batch analyzer**. Analyze records with stable equality, single-use streams and owned executor lifecycles. Assessment: missing.

### JavaScript: source-backed draft course

Prerequisites: Ability to edit text and run a local program; begin with the foundations module. Prior programming literacy is recommended for the compact overview.

- **javascript-00 — JavaScript foundations: values, functions and iteration**. Objectives: Identify how JavaScript represents values, strings, equality and function calls. Trace the reference’s iteration idiom and explain its mutation or ownership behavior. Write a conditional, a terminating loop and a small function using the dedicated beginner readings. Practice: Use the JavaScript overview to annotate a short sequence-processing function: input types, iteration, equality and failure path. Record syntax you still need to learn before proceeding. Readings: `javascript-fundamentals` (content_catalog; JavaScript fundamentals); `javascript-path-01-values` (content_catalog; JavaScript values); `javascript-path-02-conditions` (content_catalog; JavaScript conditions); `javascript-path-03-loops` (content_catalog; JavaScript loops); `javascript-path-04-functions` (content_catalog; JavaScript functions).
- **javascript-01 — Modules and hosts**. Objectives: Separate live module bindings from host-defined module resolution. Practice: Specify module imports for one chosen host and describe a dynamic-import failure path. Readings: `generated-javascript-modules-v1` (reference_library; JavaScript modules: exports, resolution, and loading).
- **javascript-02 — Closures and retained state**. Objectives: Trace captured bindings and identify retained objects. Practice: Design independent search sessions and explain how callbacks retain and release session state. Readings: `ref-gapfill-v1-javascript-closures-capture-bindings-and-preserve-reachable-state` (reference_library; Closures capture bindings and preserve reachable state).
- **javascript-03 — Receivers and prototypes**. Objectives: Explain receiver loss and own versus inherited properties. Practice: Trace an extracted method and design a safe callback with explicit receiver behavior. Readings: `ref-gapfill-v1-javascript-this-binding-prototypes-and-property-lookup` (reference_library; This binding prototypes and property lookup).
- **javascript-04 — Representation and operation costs**. Objectives: Distinguish sparse slots and account for Unicode representation. Explain the assigned array-mutation reading and trace its index/value or shifting behavior. Practice: Define search input behavior for holes, empty values and supplementary Unicode characters. Readings: `ref-gapfill-v1-javascript-sparse-arrays-unicode-and-operation-costs` (reference_library; Sparse arrays Unicode and operation costs); `corpus-js-array-remove-while-iterating` (curriculum; Removing elements while looping).
- **javascript-05 — Promises and error propagation**. Objectives: Explain promise continuations and propagate asynchronous failures. Practice: Trace independent requests under Promise.all and describe rejection without assuming cancellation. Readings: `generated-javascript-promises-async-v1` (reference_library; JavaScript promises, async functions, and error flow).
- **javascript-06 — Cancellation and fetch boundaries**. Objectives: Separate cancellation, transport failure and HTTP response handling. Practice: Design latest-request-wins search behavior with AbortSignal and stale-result protection. Readings: `ref-gapfill-v1-javascript-async-cancellation-and-fetch-error-boundaries` (reference_library; Async cancellation and fetch error boundaries).

Capstone: **An asynchronous searchable view**. Build a modular search workflow with explicit state ownership, cancellation and host boundaries. Assessment: missing.

### Python: source-backed draft course

Prerequisites: Ability to edit text and run a local program; begin with the foundations module. Prior programming literacy is recommended for the compact overview.

- **python-00 — Python foundations: values, functions and iteration**. Objectives: Identify how Python represents values, strings, equality and function calls. Trace the reference’s iteration idiom and explain its mutation or ownership behavior. Write a conditional, a terminating loop and a small function using the dedicated beginner readings. Practice: Use the Python overview to annotate a short sequence-processing function: input types, iteration, equality and failure path. Record syntax you still need to learn before proceeding. Readings: `python-fundamentals` (content_catalog; Python fundamentals); `python-path-01-values` (content_catalog; Python values); `python-path-02-conditions` (content_catalog; Python conditions); `python-path-03-loops` (content_catalog; Python loops); `python-path-04-functions` (content_catalog; Python functions).
- **python-01 — Environments and imports**. Objectives: Distinguish interpreter selection, dependency installation and import resolution. Practice: Record a reproducible environment and diagnose an import using the wrong interpreter. Readings: `ref-gapfill-v1-python-virtual-environments-packaging-and-imports` (reference_library; Virtual environments packaging and imports).
- **python-02 — Arguments and shared defaults**. Objectives: Explain argument binding and definition-time default evaluation. Practice: Specify a session function whose optional collection does not leak state between calls. Readings: `ref-gapfill-v1-python-argument-binding-defaults-and-shared-mutable-state` (reference_library; Argument binding defaults and shared mutable state).
- **python-03 — Iteration and exhaustion**. Objectives: Separate iterable factories from single-use iterator state. Practice: Design a lazy summarizer input and explain behavior after partial and repeated consumption. Readings: `ref-gapfill-v1-python-iterators-generators-and-exhaustion` (reference_library; Iterators generators and exhaustion).
- **python-04 — Cleanup and exceptions**. Objectives: Describe context-manager exit and exception propagation. Practice: Plan file ownership and cleanup when parsing fails halfway through a stream. Readings: `ref-gapfill-v1-python-context-managers-exception-propagation-and-cleanup` (reference_library; Context managers exception propagation and cleanup).
- **python-05 — Data models and validation**. Objectives: Separate generated dataclass methods and type hints from runtime validation. Practice: Specify a record model with independent mutable fields and explicit external-input checks. Readings: `ref-gapfill-v1-python-dataclasses-typing-and-validation-boundaries` (reference_library; Dataclasses typing and validation boundaries).
- **python-06 — Async task ownership**. Objectives: Identify blocking operations and define task cancellation cleanup. Practice: Extend the summarizer plan with concurrent I/O while preserving failure and cleanup behavior. Readings: `ref-gapfill-v1-python-asyncio-tasks-blocking-code-and-cancellation` (reference_library; Asyncio tasks blocking code and cancellation).

Capstone: **A streaming record summarizer**. Build a packaged summarizer with lazy input, isolated state and deterministic cleanup. Assessment: missing.

### Ruby: source-backed draft course

Prerequisites: Ability to edit text and run a local program; begin with the foundations module. Prior programming literacy is recommended for the compact overview.

- **ruby-00 — Ruby foundations: values, functions and iteration**. Objectives: Identify how Ruby represents values, strings, equality and function calls. Trace the reference’s iteration idiom and explain its mutation or ownership behavior. Practice: Use the Ruby overview to annotate a short sequence-processing function: input types, iteration, equality and failure path. Record syntax you still need to learn before proceeding. Readings: `ruby-fundamentals` (content_catalog; Ruby fundamentals).
- **ruby-01 — Bundler and isolated checks**. Objectives: Separate declared requirements from locked resolution and isolate example state. Practice: Specify bundle execution and fixtures without relying on global gems or test order. Readings: `ref-gapfill-v1-ruby-bundler-gemfile-lockfiles-and-rspec-boundaries` (reference_library; Bundler Gemfile lockfiles and RSpec boundaries).
- **ruby-02 — Blocks and callable control flow**. Objectives: Explain arity and return behavior for blocks, Procs and lambdas. Practice: Choose a callable contract for deferred report filters and trace an escaping return. Readings: `ref-gapfill-v1-ruby-blocks-procs-lambdas-and-return-behavior` (reference_library; Blocks Procs lambdas and return behavior).
- **ruby-03 — Modules and mutation**. Objectives: Inspect method lookup and distinguish shallow freezing from recursive immutability. Practice: Design a reporting mixin and document which objects each method can mutate. Readings: `ref-gapfill-v1-ruby-modules-method-lookup-and-mutation-contracts` (reference_library; Modules method lookup and mutation contracts).
- **ruby-04 — Enumerable and key stability**. Objectives: Separate lazy iteration from concurrency and preserve Hash-key stability. Practice: Plan a lazy report pipeline and compare allocations with eager materialization. Readings: `ref-gapfill-v1-ruby-enumerable-lazy-iteration-hash-keys-and-fibers` (reference_library; Enumerable lazy iteration Hash keys and Fibers).
- **ruby-05 — Dynamic-programming state ownership**. Objectives: Allocate independent mutable DP rows and include all state in memoization keys. Practice: Design a small inventory allocation planner with independent rows and explicit state dependencies. Readings: `ref-gapfill-v1-ruby-ruby-dynamic-programming-state-ownership-and-costs` (reference_library; Ruby dynamic programming state ownership and costs).

Capstone: **A lazy inventory report**. Build a bundled report tool with callable contracts, stable Hash keys and independently owned state. Assessment: missing.

### Rust: source-backed draft course

Prerequisites: Ability to edit text and run a local program; begin with the foundations module. Prior programming literacy is recommended for the compact overview.

- **rust-00 — Rust foundations: values, functions and iteration**. Objectives: Identify how Rust represents values, strings, equality and function calls. Trace the reference’s iteration idiom and explain its mutation or ownership behavior. Practice: Use the Rust overview to annotate a short sequence-processing function: input types, iteration, equality and failure path. Record syntax you still need to learn before proceeding. Readings: `rust-fundamentals` (content_catalog; Rust fundamentals).
- **rust-01 — Cargo and version provenance**. Objectives: Distinguish edition, compiler, dependency and optimization-profile effects. Practice: Record a project baseline and a benchmark plan that does not treat debug timings as a language guarantee. Readings: `ref-gapfill-v1-rust-edition-compiler-cargo-profiles-and-algorithm-claims` (reference_library; Edition compiler Cargo profiles and algorithm claims).
- **rust-02 — Ownership and borrow diagnostics**. Objectives: Trace moves and conflicting borrows before choosing a repair. Practice: Annotate owners and borrows in a graph API and explain one repair without blindly cloning. Readings: `ref-gapfill-v1-rust-ownership-moves-borrows-and-diagnostic-repair` (reference_library; Ownership moves borrows and diagnostic repair).
- **rust-03 — Lifetimes and trait bounds**. Objectives: Relate returned references to input lifetimes and explain trait requirements. Practice: Specify a borrowed lookup result and show why it cannot outlive graph storage. Readings: `ref-gapfill-v1-rust-lifetimes-trait-bounds-and-borrowed-return-values` (reference_library; Lifetimes trait bounds and borrowed return values).
- **rust-04 — Interior mutability and sharing**. Objectives: Distinguish runtime borrow checking, reference counting and thread-safety bounds. Practice: Compare a single-threaded shared model with a synchronized threaded model and state each invariant. Readings: `ref-gapfill-v1-rust-interior-mutability-send-sync-and-shared-state` (reference_library; Interior mutability Send Sync and shared state).
- **rust-05 — Traversal state and partial failure**. Objectives: Define discovery state and account for frontier ownership and partial failure. Practice: Specify graph exploration for cycles, disconnected vertices and a failed expansion. Readings: `ref-gapfill-v1-rust-shared-traversal-discovery-state-and-partial-failure` (reference_library; Traversal discovery state and partial failure).
- **rust-06 — Unsafe boundaries**. Objectives: Identify caller obligations at unsafe and FFI boundaries. Practice: Write a boundary contract for an optional foreign graph importer without claiming safe syntax proves validity. Readings: `ref-gapfill-v1-rust-unsafe-contracts-ffi-and-representation` (reference_library; Unsafe contracts FFI and representation).

Capstone: **A borrowing-aware graph explorer**. Build a graph explorer with explicit ownership, borrowed query results and documented shared-state contracts. Assessment: missing.

### TypeScript: source-backed draft course

Prerequisites: JavaScript basics before the TypeScript type-system sequence.

- **typescript-00 — TypeScript foundations: values, functions and iteration**. Objectives: Identify how TypeScript represents values, strings, equality and function calls. Trace the reference’s iteration idiom and explain its mutation or ownership behavior. Practice: Use the TypeScript overview to annotate a short sequence-processing function: input types, iteration, equality and failure path. Record syntax you still need to learn before proceeding. Readings: `typescript-fundamentals` (content_catalog; TypeScript fundamentals).
- **typescript-01 — Compiler and module configuration**. Objectives: Separate emitted target, module resolution and strictness settings. Practice: Record a tsconfig baseline and explain a library type available without matching runtime support. Readings: `ref-gapfill-v1-typescript-tsconfig-target-strictness-modules-and-declarations` (reference_library; Tsconfig target strictness modules and declarations).
- **typescript-02 — Erasure and external data**. Objectives: Explain erased types and validate external unknown values. Practice: Specify an input parser that rejects malformed records instead of asserting their type. Readings: `ref-gapfill-v1-typescript-type-erasure-assertions-enums-and-external-data` (reference_library; Type erasure assertions enums and external data).
- **typescript-03 — Narrowing and exhaustive states**. Objectives: Model alternatives with discriminants and check exhaustive branches. Practice: Design loading, success and failure states and describe the compiler response to a new variant. Readings: `ref-gapfill-v1-typescript-discriminated-unions-narrowing-and-exhaustiveness` (reference_library; Discriminated unions narrowing and exhaustiveness).
- **typescript-04 — Generic transformations**. Objectives: Preserve relationships using constraints and distinguish type computation from runtime work. Practice: Specify a typed record projection and boundary cases for optional fields. Readings: `ref-gapfill-v1-typescript-generic-constraints-mapped-and-conditional-types` (reference_library; Generic constraints mapped and conditional types).
- **typescript-05 — Function compatibility**. Objectives: Explain structural compatibility and callback variance limits. Practice: Compare callback signatures under the selected strictness settings and identify unsafe assumptions. Readings: `ref-gapfill-v1-typescript-function-variance-structural-compatibility-and-soundness-limits` (reference_library; Function variance structural compatibility and soundness limits).
- **typescript-06 — Explicit dynamic-programming states**. Objectives: Separate uncomputed states from legitimate zero and unreachable results. Practice: Design a memo table with explicit state variants and trace dependency order. Readings: `ref-gapfill-v1-typescript-dynamic-programming-with-explicit-unknown-states` (reference_library; Dynamic programming with explicit unknown states).

Capstone: **A typed external-data explorer**. Build a typed explorer that validates unknown input and models state transitions exhaustively. Assessment: missing.

### HTML: source-backed draft course

Prerequisites: Ability to edit a text file and inspect a browser DOM; no programming prerequisite.

- **html-01 — Parsed structure and attributes**. Objectives: Distinguish source markup, repaired DOM, boolean attributes and live properties. Practice: Inspect invalid nesting and disabled="false" in a local page; record source versus parsed behavior. Readings: `ref-gapfill-v1-html-element-content-models-attributes-and-live-properties` (reference_library; Element content models attributes and live properties).
- **html-02 — Native semantics and keyboard access**. Objectives: Choose native controls and explain why ARIA does not supply interaction. Practice: Outline headings and landmarks and walk through keyboard focus without hiding the focused element. Readings: `ref-gapfill-v1-html-native-semantics-keyboard-focus-and-aria` (reference_library; Native semantics keyboard focus and ARIA).
- **html-03 — Forms and validation boundaries**. Objectives: Associate persistent labels and distinguish browser validation from server checks. Practice: Design named controls, autocomplete and associated errors; document bypassed client validation. Readings: `ref-gapfill-v1-html-forms-labels-validation-and-server-boundaries` (reference_library; Forms labels validation and server boundaries).
- **html-04 — Lifecycle and capabilities**. Objectives: Separate HTML semantics, DOM APIs and permission-dependent capabilities. Practice: Write a script-loading and fallback plan that leaves the form usable when an optional API is absent. Readings: `ref-gapfill-v1-html-html-dom-apis-lifecycle-permissions-and-compatibility` (reference_library; HTML DOM APIs lifecycle permissions and compatibility).

Capstone: **An accessible registration document**. Author a semantic registration page with labeled controls, usable errors and documented browser boundaries. Assessment: missing.

### CSS: source-backed draft course

Prerequisites: Basic HTML structure and browser style inspection.

- **css-01 — Cascade and value stages**. Objectives: Resolve declarations using cascade order before specificity and separate inheritance. Practice: Design a layer policy and explain one conflicting declaration through computed and used values. Readings: `ref-gapfill-v1-css-cascade-layers-specificity-inheritance-and-values` (reference_library; Cascade layers specificity inheritance and values).
- **css-02 — Selectors and interaction states**. Objectives: Distinguish selector relationships, media queries and container queries. Practice: Specify focus, hover and reduced-motion states plus a content-driven responsive breakpoint. Readings: `ref-gapfill-v1-css-selectors-responsive-queries-and-interaction-states` (reference_library; Selectors responsive queries and interaction states).
- **css-03 — Box constraints and layout**. Objectives: Diagnose intrinsic sizing and automatic minimum constraints in flex and grid. Practice: Plan a form layout with long unbroken content and document the intended overflow and shrink behavior. Readings: `ref-gapfill-v1-css-box-sizing-intrinsic-sizes-flex-and-grid-constraints` (reference_library; Box sizing intrinsic sizes flex and grid constraints).
- **css-04 — Progressive enhancement and support**. Objectives: Separate recognized syntax from demonstrated behavior on a browser baseline. Practice: Specify a baseline layout and optional @supports enhancement; include zoom, keyboard and overflow checks. Readings: `ref-gapfill-v1-css-browser-support-progressive-enhancement-and-feature-status` (reference_library; Browser support progressive enhancement and feature status).

Capstone: **A resilient responsive form layout**. Style a semantic form with a deliberate cascade, content-driven layout and usable fallback behavior. Assessment: missing.
