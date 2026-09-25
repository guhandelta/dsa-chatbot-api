"""Content catalog for the three learning tracks.

TRACKS
------
  language   — language fundamentals & data structures specific to ONE language
               (Python dicts, Java Collections, Rust ownership, C pointers...)
  dsa        — LeetCode / HackerRank problems (language-agnostic statement,
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
    source: leetcode          # leetcode | hackerrank | authored
    io_mode: function         # function | stdio  (stdio = HackerRank style)
    ---
    # Title — Difficulty — Category

Files without front matter fall back to the original H1 format and default to
track=dsa, which keeps every previously authored problem working unchanged.
"""
import re
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

CONTENT_DIR = Path(__file__).resolve().parents[2] / "data" / "content"
LEGACY_DIR = Path(__file__).resolve().parents[2] / "data" / "dsa_problems"

TRACKS = ("language", "dsa", "algorithm")
DIFFICULTIES = ("Easy", "Medium", "Hard")

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
    source: str = "authored"             # leetcode | hackerrank | authored
    io_mode: str = "function"            # function | stdio
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
        if key == "algorithms":
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
    order = {d: i for i, d in enumerate(DIFFICULTIES)}
    out.sort(key=lambda c: (c.track, order.get(c.difficulty, 9), c.title))
    return out


def filter_content(
    track: str | None = None,
    language: str | None = None,
    difficulty: str | None = None,
    algorithm: str | None = None,
    source: str | None = None,
) -> list[ContentMeta]:
    items = list_content()
    if track:
        items = [c for c in items if c.track == track]
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
    return items


def find_path(content_id: str) -> Path | None:
    for directory in _all_dirs():
        candidate = directory / f"{content_id}.md"
        if candidate.is_file():
            return candidate
    return None


def read_content(content_id: str) -> str:
    """Full markdown (front matter stripped) for one item."""
    path = find_path(content_id)
    if not path:
        return ""
    _, body = _parse_front_matter(path.read_text())
    return body


def content_exists(content_id: str) -> bool:
    return find_path(content_id) is not None


def known_algorithms() -> list[str]:
    """Every algorithm tag in use, for the algorithm-track picker."""
    tags: set[str] = set()
    for c in list_content():
        tags.update(c.algorithms)
    return sorted(tags)


def known_languages() -> list[str]:
    return ["python", "javascript", "java", "cpp", "c", "rust"]


def track_summary() -> list[dict]:
    """Counts per track, for the track-selection screen."""
    items = list_content()
    labels = {
        "language": "Language Fundamentals",
        "dsa": "DSA Problems",
        "algorithm": "Algorithms",
    }
    blurbs = {
        "language": "Syntax, built-in data structures, and idioms for your chosen language.",
        "dsa": "LeetCode and HackerRank problems, solved and reviewed.",
        "algorithm": "Learn an algorithm as a concept, then apply it at increasing difficulty.",
    }
    return [
        {
            "track": t,
            "label": labels[t],
            "blurb": blurbs[t],
            "count": len([c for c in items if c.track == t]),
        }
        for t in TRACKS
    ]


def load_test_cases(content_id: str) -> tuple[list, list, dict, str]:
    """Returns (args_list, expected_list, fn_names, io_mode) for a problem.

    Empty lists mean the problem has no executable tests (e.g. linked-list
    inputs that have no JSON representation) — callers must fall back to
    review-only feedback rather than claiming verification.
    """
    import json as _json

    path = find_path(content_id)
    if not path:
        return [], [], {}, "function"
    front, _ = _parse_front_matter(path.read_text())
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
    if front.get("fn_javascript"):
        fns["javascript"] = front["fn_javascript"]
    return (
        [c["args"] for c in cases],
        [c["expected"] for c in cases],
        fns,
        front.get("io_mode", "function"),
    )


def reference_solution(content_id: str, language: str = "python") -> tuple[str, str] | None:
    """Returns (code, function_name) of the verified reference solution.
    This is what a student's submission is diffed against during fuzzing."""
    import re as _re

    path = find_path(content_id)
    if not path:
        return None
    _, body = _parse_front_matter(path.read_text())
    label = {"python": "Python", "javascript": "JavaScript"}.get(language)
    if not label:
        return None
    m = _re.search(rf"### {label}\n```[a-z]*\n(.*?)```", body, _re.DOTALL)
    if not m:
        return None
    code = m.group(1)
    front, _ = _parse_front_matter(path.read_text())
    fn = front.get(f"fn_{language}")
    if not fn:
        pattern = r"^\s*def\s+(\w+)" if language == "python" else r"^\s*function\s+(\w+)"
        fm = _re.search(pattern, code, _re.MULTILINE)
        fn = fm.group(1) if fm else None
    return (code, fn) if fn else None
