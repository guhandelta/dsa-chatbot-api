"""Learning paths: one shared spine, then per-language depth modules.

    Path (language)
     └─ Stage 1-12 (shared spine)   the same twelve stages in every language
         └─ Node                    lesson + checks (quiz) + graded exercise + practice set
     └─ Depth modules (13+)         what makes this language this language

Each spine node reuses existing content: the `<language>-path-NN-<slug>`
lesson/exercise file when it exists (Java, JavaScript, Python today), the
language fundamentals page, and knowledge-base rows whose data structure
matches the stage. Depth modules draw their lessons from the language's
reference rows (including the gap-fill references) by keyword.

Mastery rule: a node is complete when its graded exercise has passed AND its
checks score at least two thirds. A node that has only one of the two is
judged on that one; a node with neither is shown as not yet available and is
skipped when choosing the learner's current position.
"""
from dataclasses import dataclass, field
from functools import lru_cache

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LearningEvent

MASTERY_RATIO = 2 / 3

# Which problem difficulties suit a level. The first one is the "apply"
# difficulty; the others are stretch work.
LEVEL_DIFFICULTIES = {
    "L0": ("Easy",), "L1": ("Easy",), "L2": ("Easy", "Medium"),
    "L3": ("Medium", "Hard"), "L4": ("Medium", "Hard"),
}
LEVEL_LABELS = {
    "L0": "Syntax and first programs", "L1": "Core constructs", "L2": "Data modelling",
    "L3": "Recursion, complexity and depth", "L4": "Language mastery",
}
RUNNABLE = ("python", "javascript", "java", "c", "cpp", "rust")
LANGUAGE_LABELS = {
    "python": "Python", "javascript": "JavaScript", "java": "Java", "typescript": "TypeScript",
    "c": "C", "cpp": "C++", "rust": "Rust", "go": "Go", "csharp": "C#", "ruby": "Ruby",
}


@dataclass(frozen=True)
class Stage:
    number: int
    slug: str
    title: str
    level: str
    # Knowledge-base data_structure / data_structure_id values that belong here.
    data_structures: tuple[str, ...]
    problems: tuple[str, ...] = ()
    # Problems the plan calls for that the bank does not have yet.
    planned: tuple[str, ...] = ()


SPINE: tuple[Stage, ...] = (
    Stage(1, "values", "Values and arithmetic", "L1",
          ("intbits", "bitwise-operations", "bits", "enum", "symbol", "typealias", "typedef"),
          ("missing-number", "number-of-1-bits", "sum-of-two-integers")),
    Stage(2, "conditions", "Conditions and boolean logic", "L1", ("range", "union"),
          ("binary-search", "find-minimum-in-rotated-sorted-array")),
    Stage(3, "loops", "Loops and accumulation", "L1",
          ("enumerator-and-lazy-evaluation", "searching"),
          ("best-time-to-buy-and-sell-stock", "counting-bits", "maximum-subarray")),
    Stage(4, "functions", "Functions and contracts", "L1",
          ("function-pointer", "interface", "typealias"),
          ("reverse-bits", "climbing-stairs")),
    Stage(5, "strings", "Strings and iteration", "L1",
          ("string", "regexp", "regexp-regular-expressions"),
          ("word-break", "longest-common-subsequence"), ("Valid Anagram (Easy)",)),
    Stage(6, "arrays", "Arrays and lists", "L1",
          ("array", "dynamic-array", "array_patterns", "typedarray", "arraybuffer", "tuple", "grid",
           "matrix-and-vector-require-matrix"),
          ("contains-duplicate", "best-time-to-buy-and-sell-stock", "product-of-array-except-self",
           "maximum-product-subarray")),
    Stage(7, "maps", "Maps and frequency counting", "L2",
          ("map", "hash-table", "weakmap", "record", "json", "collections"),
          ("two-sum", "contains-duplicate", "3sum"), ("Group Anagrams (Medium)", "LRU Cache (Hard)")),
    Stage(8, "sets", "Sets and equality", "L2",
          ("set", "bloom-filter", "disjoint-set", "union_find", "weakset"),
          ("contains-duplicate", "missing-number"), ("Longest Consecutive Sequence (Medium)",)),
    Stage(9, "objects", "Objects, state, and references", "L2",
          ("object", "struct", "structs-and-unions", "struct-and-openstruct", "classes-and-modules",
           "pointer", "void-pointer", "linked-list", "linked_list", "doubly-linked-list", "data-ruby-3-2"),
          ("reverse-linked-list",)),
    Stage(10, "validation", "Validation and failure contracts", "L2",
          ("date", "dataview", "time-and-date-structures", "date-time-and-datetime-require-date"),
          ("binary-search", "search-in-rotated-sorted-array")),
    Stage(11, "recursion", "Recursion and base cases", "L3",
          ("recursion-dp", "recursion_dp", "binary-tree", "binary_tree", "binary-search-tree", "trie",
           "graph-traversal", "graph", "graph-adjacency-list", "greedy_graphs"),
          ("climbing-stairs", "coin-change", "combination-sum-iv", "word-break"), ("N-Queens (Hard)",)),
    Stage(12, "complexity", "Complexity and the DSA bridge", "L3",
          ("heap", "priority-queue", "queue", "deque", "stack", "sorting", "segment-tree", "fenwick-tree",
           "range_query", "avl-tree", "red-black-tree"),
          ("two-sum", "container-with-most-water", "longest-increasing-subsequence", "3sum"),
          ("Kth Largest Element (Medium)", "Merge k Sorted Lists (Hard)")),
)


@dataclass(frozen=True)
class Module:
    slug: str
    title: str
    level: str
    keywords: tuple[str, ...] = field(default=())


def _m(slug, title, level, *keywords):
    return Module(slug, title, level, keywords or (slug.replace("-", " "),))


DEPTH_MODULES: dict[str, tuple[Module, ...]] = {
    "python": (
        _m("iterators-generators", "Iterators and generators", "L3", "generator", "iterator", "yield"),
        _m("context-managers", "Context managers", "L3", "context manager", "with statement", "__exit__"),
        _m("dataclasses", "Dataclasses", "L3", "dataclass"),
        _m("typing", "Type hints", "L3", "typing", "type hint", "annotation"),
        _m("exceptions", "Exceptions and propagation", "L3", "exception", "raise", "traceback"),
        _m("asyncio", "asyncio", "L4", "asyncio", "await", "event loop"),
        _m("packaging", "Imports, packaging and venv", "L4", "import", "module", "venv", "package"),
        _m("pytest", "Testing with pytest", "L4", "pytest", "fixture"),
    ),
    "java": (
        _m("generics", "Generics and variance", "L3", "generic", "wildcard", "variance"),
        _m("collections-contracts", "Collections contracts", "L3", "equals", "hashcode", "compareto"),
        _m("streams", "Streams", "L3", "stream"),
        _m("concurrency", "Concurrency and CompletableFuture", "L4", "thread", "completablefuture", "interrupt"),
        _m("junit", "JUnit", "L4", "junit"),
    ),
    "javascript": (
        _m("closures-this-prototypes", "Closures, this and prototypes", "L3", "closure", "prototype", "this"),
        _m("coercion", "Coercion", "L3", "coercion", "==="),
        _m("event-loop", "The event loop", "L3", "event loop", "microtask"),
        _m("promises-async", "Promises and async", "L4", "promise", "async", "await"),
        _m("abort-controller", "AbortController", "L4", "abortcontroller", "abort"),
        _m("modules", "Modules", "L4", "module", "import", "export"),
    ),
    "typescript": (
        _m("narrowing", "Narrowing", "L3", "narrowing", "discriminated", "type guard"),
        _m("generics-inference", "Generics and inference", "L3", "generic", "inference"),
        _m("mapped-conditional-types", "Mapped and conditional types", "L4", "mapped", "conditional type"),
        _m("runtime-boundary", "The runtime boundary", "L4", "runtime", "validation"),
        _m("tsconfig", "tsconfig", "L4", "tsconfig", "strict"),
    ),
    "c": (
        _m("pointers-storage", "Storage duration and pointers", "L3", "pointer", "storage duration"),
        _m("ownership-cleanup", "Ownership and cleanup", "L3", "free", "malloc", "ownership"),
        _m("strings-bounds", "Strings and bounds", "L3", "bounds", "strncpy", "null terminator"),
        _m("integer-ub", "Integer undefined behaviour", "L4", "undefined behaviour", "overflow"),
        _m("errno", "errno and error reporting", "L4", "errno"),
        _m("build-link", "Build and link", "L4", "linker", "compile", "header"),
    ),
    "cpp": (
        _m("raii-smart-pointers", "RAII and smart pointers", "L3", "raii", "unique_ptr", "shared_ptr"),
        _m("copy-move", "Copy and move", "L3", "move", "copy constructor"),
        _m("iterator-invalidation", "Iterator invalidation", "L3", "invalidation", "iterator"),
        _m("comparators", "Comparators and ordering", "L3", "comparator", "strict weak ordering"),
        _m("templates-concepts", "Templates and concepts", "L4", "template", "concept"),
        _m("exception-safety", "Exception safety", "L4", "exception safety", "noexcept"),
    ),
    "rust": (
        _m("ownership-borrowing", "Ownership and borrowing", "L3", "ownership", "borrow"),
        _m("lifetimes", "Lifetimes", "L3", "lifetime"),
        _m("traits-generics", "Traits and generics", "L3", "trait", "generic"),
        _m("error-handling", "Error handling", "L3", "result", "error", "? operator"),
        _m("interior-mutability", "Interior mutability, Send and Sync", "L4", "refcell", "send", "sync"),
        _m("async", "Async Rust", "L4", "async", "future", "pin"),
        _m("unsafe-ffi", "unsafe and FFI", "L4", "unsafe", "ffi"),
    ),
    "go": (
        _m("slices-maps", "Slices and maps semantics", "L3", "slice", "map"),
        _m("interfaces-method-sets", "Interfaces and method sets", "L3", "interface", "method set"),
        _m("errors", "Errors", "L3", "error", "wrap"),
        _m("goroutines-channels", "Goroutines and channels", "L4", "goroutine", "channel"),
        _m("context", "context", "L4", "context", "cancellation"),
        _m("generics", "Generics", "L4", "generic", "type parameter"),
    ),
    "csharp": (
        _m("value-reference", "Value vs reference", "L3", "value type", "reference type", "struct"),
        _m("generics", "Generics", "L3", "generic", "constraint"),
        _m("linq", "LINQ deferred execution", "L3", "linq", "deferred"),
        _m("records-patterns", "Records and pattern matching", "L4", "record", "pattern matching"),
        _m("async-cancellation", "Async and cancellation", "L4", "async", "cancellation"),
    ),
    "ruby": (
        _m("blocks-procs-lambdas", "Blocks, procs and lambdas", "L3", "block", "proc", "lambda"),
        _m("enumerable-lazy", "Enumerable and lazy", "L3", "enumerable", "lazy"),
        _m("method-lookup-modules", "Method lookup and modules", "L3", "method lookup", "module", "mixin"),
        _m("mutation", "Mutation and frozen objects", "L3", "mutation", "freeze", "frozen"),
        _m("bundler", "Bundler", "L4", "bundler", "gem"),
        _m("rspec", "RSpec", "L4", "rspec"),
    ),
}


def stage_node_id(language: str, stage: Stage) -> str:
    return f"{language}:stage-{stage.number:02d}"


def module_node_id(language: str, module: Module) -> str:
    return f"{language}:module-{module.slug}"


def stage_exercise_id(language: str, stage: Stage) -> str | None:
    from app.services.content_catalog import find_path
    content_id = f"{language}-path-{stage.number:02d}-{stage.slug}"
    return content_id if find_path(content_id) else None


def _catalog():
    from app.services.content_catalog import filter_content
    return {c.id: c for c in filter_content()}


def _row_title(row: dict) -> str:
    return row["document"].split("\n", 1)[0][:160]


@lru_cache(maxsize=64)
def _module_sources(language: str, keywords: tuple[str, ...], library_version) -> tuple[tuple[str, str], ...]:
    """(row id, title) of answer-free reference rows that teach this module."""
    from app.services.reference_library import eligible, records
    found = []
    for row in records():
        meta = row["metadata"]
        if meta.get("language") != language or meta.get("subject") != language or not eligible(row):
            continue
        haystack = (_row_title(row) + " " + str(meta.get("data_structure", ""))).lower()
        if any(k.lower() in haystack for k in keywords):
            found.append((row["id"], _row_title(row)))
        if len(found) >= 4:
            break
    return tuple(found)


def module_sources(language: str, module: Module) -> list[dict]:
    from app.services.reference_library import version
    return [{"id": rid, "title": title} for rid, title in _module_sources(language, module.keywords, version())]


def practice_set(stage: Stage, level: str | None = None) -> list[dict]:
    """Executable problems for a stage, at the difficulties its level suits."""
    catalog = _catalog()
    allowed = LEVEL_DIFFICULTIES[level or stage.level]
    out = []
    for pid in stage.problems:
        item = catalog.get(pid)
        if item is None or item.difficulty not in allowed:
            continue
        out.append({"id": pid, "title": item.title, "difficulty": item.difficulty,
                    "role": "apply" if item.difficulty == allowed[0] else "stretch"})
    return out


def _quiz_count(language: str, node: dict) -> int:
    from app.services import quiz
    return quiz.pool_size(language, node)


def nodes(language: str) -> list[dict]:
    """Every node of the language's path, in learning order."""
    from app.services.content_catalog import find_path
    out = []
    fundamentals = f"{language}-fundamentals" if find_path(f"{language}-fundamentals") else None
    for stage in SPINE:
        exercise = stage_exercise_id(language, stage)
        lessons = [x for x in (exercise, fundamentals) if x]
        out.append({
            "id": stage_node_id(language, stage), "kind": "stage", "stage": stage.number,
            "order": stage.number, "slug": stage.slug, "title": stage.title, "level": stage.level,
            "exercise_id": exercise, "lesson_ids": lessons, "data_structures": list(stage.data_structures),
            "practice": practice_set(stage), "planned_problems": list(stage.planned),
        })
    for index, module in enumerate(DEPTH_MODULES.get(language, ()), start=13):
        sources = module_sources(language, module)
        out.append({
            "id": module_node_id(language, module), "kind": "module", "stage": None, "order": index,
            "slug": module.slug, "title": module.title, "level": module.level, "exercise_id": None,
            "lesson_ids": [s["id"] for s in sources], "lesson_sources": sources,
            "keywords": list(module.keywords), "data_structures": [], "practice": [],
            "planned_problems": [],
        })
    for node in out:
        node["checks_available"] = _quiz_count(language, node)
    return out


def find_node(language: str, node_id: str) -> dict | None:
    return next((n for n in nodes(language) if n["id"] == node_id), None)


def node_for_exercise(content_id: str) -> tuple[str, Stage] | None:
    """The (language, stage) whose graded exercise this content id is."""
    for stage in SPINE:
        suffix = f"-path-{stage.number:02d}-{stage.slug}"
        if content_id.endswith(suffix):
            return content_id[: -len(suffix)], stage
    return None


def readiness(language: str) -> dict:
    """What the existing content can support for this language today."""
    from app.services.code_runner import available_languages
    path = nodes(language)
    spine = sum(1 for n in path if n["kind"] == "stage" and n["exercise_id"])
    modules = [n for n in path if n["kind"] == "module"]
    depth = sum(1 for n in modules if n["lesson_ids"])
    quiz_items = sum(n["checks_available"] for n in path)
    runner = language in RUNNABLE and bool(available_languages().get(language))
    if spine == len(SPINE) and runner and quiz_items:
        verdict = "launch-ready"
    elif not runner and quiz_items:
        verdict = "quiz-led"
    elif runner and (depth or quiz_items):
        verdict = "next-wave"
    else:
        verdict = "needs-authoring"
    return {"language": language, "label": LANGUAGE_LABELS.get(language, language),
            "spine_stages": spine, "spine_total": len(SPINE), "depth_lessons": depth,
            "depth_total": len(modules), "quiz_items": quiz_items, "runner": runner,
            "verdict": verdict}


async def passed_exercises(session: AsyncSession, user_id: str, language: str) -> set[str]:
    return set((await session.scalars(select(LearningEvent.problem_id).where(
        LearningEvent.user_id == user_id, LearningEvent.language == language,
        LearningEvent.kind == "solved"))).all())


async def progress(session: AsyncSession, user_id: str, language: str) -> dict:
    """The learner's position: per-node mastery and the current node."""
    from app.services import quiz
    passed = await passed_exercises(session, user_id, language)
    checks = await quiz.best_scores(session, user_id, language)
    path = []
    for node in nodes(language):
        has_exercise = bool(node["exercise_id"])
        has_checks = node["checks_available"] > 0
        exercise_passed = has_exercise and node["exercise_id"] in passed
        score = checks.get(node["id"])
        checks_passed = score is not None and score >= MASTERY_RATIO
        available = has_exercise or has_checks
        complete = available and (exercise_passed or not has_exercise) and (checks_passed or not has_checks)
        path.append({**node, "available": available, "exercise_passed": exercise_passed,
                     "check_score": score, "checks_passed": checks_passed, "complete": complete,
                     "status": "complete" if complete else "in-progress"
                     if (exercise_passed or score is not None) else "not-started" if available else "unavailable"})
    countable = [n for n in path if n["available"]]
    current = next((n for n in countable if not n["complete"]), None)
    done = sum(n["complete"] for n in countable)
    return {
        "language": language, "nodes": path, "current_id": current["id"] if current else None,
        "completed": done, "total": len(countable),
        "completed_stages": [n["stage"] for n in path if n["kind"] == "stage" and n["complete"]],
        "mastery_rule": "Pass the graded exercise and score at least 2 of 3 on the checks.",
    }


async def reward_completed_stages(session: AsyncSession, user_id: str, language: str) -> list[dict]:
    """Pay the stage-completion reward once for each newly completed stage."""
    from app.core.config import settings
    from app.services.rewards import grant_once
    state = await progress(session, user_id, language)
    earned = []
    for stage in state["completed_stages"]:
        grant = await grant_once(session, user_id, f"stage:{language}:{stage}",
                                 settings.reward_stage_complete, "earn:stage")
        if grant:
            earned.append(grant)
    return earned
