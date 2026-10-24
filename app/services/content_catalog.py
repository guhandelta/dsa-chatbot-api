"""Content catalog for the three learning tracks.

TRACKS
------
  language   — language fundamentals & data structures specific to ONE language
               (Python dicts, Java Collections, Rust ownership, C pointers...)
  dsa        — practice problems (language-agnostic statement,
               solutions in all six languages)
  algorithm  — algorithms as a concept, then practised on problems of
               increasing difficulty

Each track supports both LEARN (concept explanation, RAG-grounded chat) and
PRACTICE (write code, get it executed and reviewed).

METADATA
--------
Files may declare metadata in a front-matter block:

    ---
    track: algorithm
    difficulty: Medium
    language: python          # only for track=language
    algorithms: binary-search, two-pointers
    source: authored            # authored | hackerrank | legacy-leetcode (retired label)
    io_mode: function         # function | stdio  (stdio = HackerRank style)
    ---
    # Title — Difficulty — Category

Files without front matter fall back to the original H1 format and default to
track=dsa, which keeps every previously authored problem working unchanged.
"""
import re
import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

CONTENT_DIR = Path(__file__).resolve().parents[2] / "data" / "content"
LEGACY_DIR = Path(__file__).resolve().parents[2] / "data" / "dsa_problems"

# Internal tracks — how content is stored on disk.
TRACKS = ("language", "dsa", "algorithm", "design-patterns")
DIFFICULTIES = ("Easy", "Medium", "Hard")

# Learner-facing sections — how content is presented. `dsa` aggregates the
# problems and the technique write-ups, because a learner thinks of those as
# one subject rather than two.
SECTIONS: dict[str, tuple[str, ...]] = {
    "language": ("language",),
    "dsa": ("dsa", "algorithm"),
    "design-patterns": ("design-patterns",),
}

# Progression within Language Fundamentals. Held as metadata rather than shown
# as three named doors: the selector reads it to order the path, the learner
# never has to classify themselves.
#   beginner     — syntax, entities, how code is structured in this language
#   intermediate — data structures, pairings, gotchas and fixes
#   expert       — advanced language features, and how this language expresses
#                  (or obviates) the classic design patterns
LEVELS = ("beginner", "intermediate", "expert")

_H1 = re.compile(r"^#\s+(.*?)\s+—\s+(\w+)\s+—\s+(.*)$")
_FRONT = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


class ContentMeta(BaseModel):
    id: str
    title: str
    track: str = "dsa"
    difficulty: str = "Easy"
    category: str = ""
    language: str | None = None          # set when track == "language"
    algorithms: list[str] = []           # tags linking problems to algorithms
    source: str = "authored"             # authored | hackerrank | legacy-leetcode (retired label)
    io_mode: str = "function"            # function | stdio
    # Progression level for Language Fundamentals. None means the item is not
    # level-scoped — DSA problems are ordered by `difficulty` instead, which is
    # a separate axis and must not be conflated with this one.
    order: int = 0
    prerequisites: list[str] = []
    starter_code: str = ""
    level: str | None = None
    # Design-pattern tags, parallel to `algorithms`. These cross-link a
    # language idiom page to the pattern it implements, so Expert-level
    # Language Fundamentals can glimpse a pattern without duplicating the
    # Design Patterns section.
    patterns: list[str] = []
    fn_python: str | None = None         # entry point the harness calls
    fn_javascript: str | None = None
    has_tests: bool = False              # executable test cases available


def _parse_front_matter(text: str) -> tuple[dict, str]:
    """Returns (metadata dict, body without the front matter)."""
    m = _FRONT.match(text)
    if not m:
        return {}, text
    meta: dict = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if not value or value.lower() in ("null", "none", ""):
            continue
        if key in ("algorithms", "patterns"):
            meta[key] = [v.strip() for v in value.split(",") if v.strip()]
        else:
            meta[key] = value
    return meta, text[m.end():]


def parse_file(path: Path) -> ContentMeta:
    text = path.read_text()
    front, body = _parse_front_matter(text)

    first_line = body.splitlines()[0] if body.strip() else ""
    m = _H1.match(first_line)
    if m:
        title, difficulty, category = m.group(1), m.group(2), m.group(3)
    else:
        title = front.get("title", path.stem.replace("-", " ").title())
        difficulty, category = "Easy", front.get("category", "")

    return ContentMeta(
        id=path.stem,
        title=front.get("title", title),
        track=front.get("track", "dsa"),
        difficulty=front.get("difficulty", difficulty),
        category=front.get("category", category),
        language=front.get("language"),
        algorithms=front.get("algorithms", []),
        source=front.get("source", "authored"),
        io_mode=front.get("io_mode", "function"),
        level=front.get("level"),
        order=int(front.get("order", 0)),
        prerequisites=[x.strip() for x in front.get("prerequisites", "").split(",") if x.strip()],
        starter_code=json.loads(front.get("starter_code", '""')),
        patterns=front.get("patterns", []),
        fn_python=front.get("fn_python"),
        fn_javascript=front.get("fn_javascript"),
        has_tests=bool(front.get("test_cases")),
    )


def _all_dirs() -> list[Path]:
    """Content lives in data/content/<track>/; data/dsa_problems is the legacy
    location and is still read so existing problems keep working."""
    dirs = [CONTENT_DIR / t for t in TRACKS]
    dirs.append(LEGACY_DIR)
    return [d for d in dirs if d.is_dir()]


@lru_cache(maxsize=1)
def list_content() -> list[ContentMeta]:
    out: list[ContentMeta] = []
    seen: set[str] = set()
    for directory in _all_dirs():
        for md in sorted(directory.glob("*.md")):
            if md.stem in seen:
                continue
            seen.add(md.stem)
            out.append(parse_file(md))
    from app.services.curriculum import concept_items
    for r in concept_items():
        m = r["metadata"]
        out.append(ContentMeta(
            id="corpus-" + r["id"], title=r["payload"]["concept"],
            track="language", language=m["language"], category=m["data_structure"],
            source="curriculum", level="intermediate", order=500,
        ))
    order = {d: i for i, d in enumerate(DIFFICULTIES)}
    out.sort(key=lambda c: (c.track, order.get(c.difficulty, 9), c.title))
    return out


def filter_content(
    track: str | None = None,
    language: str | None = None,
    difficulty: str | None = None,
    algorithm: str | None = None,
    source: str | None = None,
    level: str | None = None,
    pattern: str | None = None,
) -> list[ContentMeta]:
    """Filter the catalog.

    `track` accepts either a learner-facing section ("dsa") or an internal
    track name ("algorithm"), so existing callers keep working unchanged. A
    section expands to every internal track it contains.
    """
    items = list_content()
    if track:
        allowed = SECTIONS.get(track, (track,))
        items = [c for c in items if c.track in allowed]
    if language:
        # Language-track items are language-specific; dsa/algorithm items have
        # solutions in every language, so they always match.
        items = [c for c in items if c.language is None or c.language == language]
    if difficulty:
        items = [c for c in items if c.difficulty == difficulty]
    if algorithm:
        items = [c for c in items if algorithm in c.algorithms]
    if source:
        items = [c for c in items if c.source == source]
    if level:
        items = [c for c in items if c.level == level]
    if pattern:
        items = [c for c in items if pattern in c.patterns]
    return items


def find_path(content_id: str) -> Path | None:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,119}", content_id):
        return None
    for directory in _all_dirs():
        candidate = directory / f"{content_id}.md"
        if candidate.is_file():
            return candidate
    return None


def read_content(content_id: str) -> str:
    """Full markdown (front matter stripped) for one item."""
    path = find_path(content_id)
    if not path:
        from app.services.curriculum import concept_document
        return concept_document(content_id)
    _, body = _parse_front_matter(path.read_text())
    return body


def content_exists(content_id: str) -> bool:
    from app.services.curriculum import concept_document
    return find_path(content_id) is not None or bool(concept_document(content_id))


def known_algorithms() -> list[str]:
    """Every algorithm tag in use, for the algorithm-track picker."""
    tags: set[str] = set()
    for c in list_content():
        tags.update(c.algorithms)
    return sorted(tags)


def known_patterns() -> list[str]:
    """Every design-pattern tag in use, across all sections. This is what
    links a language idiom page to its Design Patterns page."""
    tags: set[str] = set()
    for c in list_content():
        tags.update(c.patterns)
    return sorted(tags)


def known_languages() -> list[str]:
    return ["python", "javascript", "java", "cpp", "c", "rust", "typescript", "ruby", "go", "csharp"]


def level_summary(language: str | None = None) -> list[dict]:
    """The three progression levels of Language Fundamentals, with counts.

    Counts are language-scoped because this is the only language-specific
    section: a Rust learner should never be shown the Python item count.
    """
    meta = {
        "beginner": ("Beginner",
                     "Syntax, entities, and how code is structured in this language."),
        "intermediate": ("Intermediate",
                         "Data structures, when to pair them, and the gotchas that bite."),
        "expert": ("Expert",
                   "Advanced language features, and how this language expresses "
                   "the classic design patterns."),
    }
    items = filter_content(track="language", language=language)
    out = []
    for level in LEVELS:
        label, blurb = meta[level]
        out.append({
            "level": level,
            "label": label,
            "blurb": blurb,
            "count": len([c for c in items if c.level == level]),
        })
    return out


def track_summary(language: str | None = None) -> list[dict]:
    """The three learner-facing sections for the choice screen.

    `dsa` aggregates the internal "dsa" and "algorithm" tracks. Language
    Fundamentals is counted against the learner's language, since it is the
    only language-specific section.
    """
    items = list_content()
    labels = {
        "language": "Language Fundamentals",
        "dsa": "Data Structures & Algorithms",
        "design-patterns": "Design Patterns",
    }
    blurbs = {
        "language": "Syntax, data structures, and idioms for your chosen language.",
        "dsa": "Original practice problems, plus the techniques behind them.",
        "design-patterns": "Choosing the right pattern, the trade-offs, and when not to use one.",
    }
    out = []
    for section, internal in SECTIONS.items():
        scoped = [c for c in items if c.track in internal]
        if section == "language" and language:
            scoped = [c for c in scoped if c.language in (None, language)]
        out.append({
            "track": section,
            "label": labels[section],
            "blurb": blurbs[section],
            "count": len(scoped),
            # The UI hides empty sections rather than leading a learner to a
            # blank page; deciding that here keeps it consistent across clients.
            "available": len(scoped) > 0,
        })
    return out


def load_test_cases(content_id: str, *, text: str | None = None) -> tuple[list, list, dict, str]:
    """Returns (args_list, expected_list, fn_names, io_mode) for a problem.

    Empty lists mean the problem has no executable tests (e.g. linked-list
    inputs that have no JSON representation) — callers must fall back to
    review-only feedback rather than claiming verification.
    """
    import json as _json

    path = find_path(content_id)
    if not path:
        return [], [], {}, "function"
    source = text if text is not None else path.read_text()
    front, _ = _parse_front_matter(source)
    raw = front.get("test_cases")
    if not raw:
        return [], [], {}, front.get("io_mode", "function")
    try:
        cases = _json.loads(raw)
    except Exception:
        return [], [], {}, front.get("io_mode", "function")
    fns = {}
    if front.get("fn_python"):
        fns["python"] = front["fn_python"]
    for lang in ("javascript", "java", "cpp", "c", "rust", "typescript", "ruby", "go", "csharp"):
        if front.get(f"fn_{lang}"):
            fns[lang] = front[f"fn_{lang}"]
    # Legacy DSA documents encode the Java method in the reference snippet.
    if "java" not in fns:
        m = re.search(r"### Java\n```java\n(.*?)```", source, re.DOTALL)
        if m:
            fn = re.search(r"public\s+(?:static\s+)?[\w<>\[\]]+\s+(\w+)\s*\(", m.group(1))
            if fn:
                fns["java"] = fn.group(1)
    return (
        [c["args"] for c in cases],
        [c["expected"] for c in cases],
        fns,
        front.get("io_mode", "function"),
    )


def reference_solution(content_id: str, language: str = "python", *, text: str | None = None) -> tuple[str, str] | None:
    """Returns (code, function_name) of the verified reference solution.
    This is what a student's submission is diffed against during fuzzing."""
    import re as _re

    path = find_path(content_id)
    if not path:
        return None
    source = text if text is not None else path.read_text()
    _, body = _parse_front_matter(source)
    label = {"python": "Python", "javascript": "JavaScript", "java": "Java"}.get(language)
    if not label:
        return None
    m = _re.search(rf"### {label}\n```[a-z]*\n(.*?)```", body, _re.DOTALL)
    if not m:
        return None
    code = m.group(1)
    front, _ = _parse_front_matter(source)
    fn = front.get(f"fn_{language}")
    if not fn:
        pattern = (r"^\s*def\s+(\w+)" if language == "python" else
                   r"(?:public\s+)?(?:static\s+)?[\w<>\[\]]+\s+(\w+)\s*\(" if language == "java" else
                   r"^\s*function\s+(\w+)")
        fm = _re.search(pattern, code, _re.MULTILINE)
        fn = fm.group(1) if fm else None
    return (code, fn) if fn else None


def comparison_mode(content_id: str, *, text: str | None = None) -> str:
    path = find_path(content_id)
    mode = _parse_front_matter(text if text is not None else path.read_text())[0].get("comparison", "exact") if path else "exact"
    if mode not in ("exact", "unordered_flat", "unordered_nested"):
        raise ValueError("Unknown exercise comparison mode")
    return mode
