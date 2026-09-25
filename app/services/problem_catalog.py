# Scans the problem markdown directory and parses each file's H1 metadata.
# Powers the /problems endpoint (so the frontend can show a dropdown) and
# full-document retrieval for the analyzer.
#
# Expected H1 format:
#   # Two Sum (LC 1) — Easy — Array, Hash Map
import re
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

PROBLEMS_DIR = Path(__file__).resolve().parents[2] / "data" / "dsa_problems"

# "# Title (LC n) — Difficulty — Category, Tags"  (em dash separated)
_H1 = re.compile(r"^#\s+(.*?)\s+—\s+(\w+)\s+—\s+(.*)$")


class ProblemMeta(BaseModel):
    id: str          # filename stem, e.g. "two-sum"
    title: str       # "Two Sum (LC 1)"
    difficulty: str  # "Easy" | "Medium" | "Hard"
    category: str    # "Array, Hash Map"


@lru_cache(maxsize=1)
def list_problems() -> list[ProblemMeta]:
    """Returns all problems sorted by difficulty then title. Cached; the
    catalog only changes when markdown files are added (and the server
    restarts on edit in dev)."""
    out: list[ProblemMeta] = []
    for md in sorted(PROBLEMS_DIR.glob("*.md")):
        first_line = md.read_text().splitlines()[0] if md.read_text() else ""
        m = _H1.match(first_line)
        if m:
            title, difficulty, category = m.group(1), m.group(2), m.group(3)
        else:
            # Fall back gracefully if a file doesn't follow the convention
            title, difficulty, category = md.stem.replace("-", " ").title(), "Unknown", ""
        out.append(
            ProblemMeta(id=md.stem, title=title, difficulty=difficulty, category=category)
        )
    order = {"Easy": 0, "Medium": 1, "Hard": 2, "Unknown": 3}
    out.sort(key=lambda p: (order.get(p.difficulty, 3), p.title))
    return out


def problem_exists(problem_id: str) -> bool:
    return (PROBLEMS_DIR / f"{problem_id}.md").is_file()


def read_problem_doc(problem_id: str) -> str:
    """Returns the entire markdown reference for a problem, or '' if missing.
    Used by the analyzer so it sees the full description + optimal solution,
    not a few similarity-retrieved chunks."""
    path = PROBLEMS_DIR / f"{problem_id}.md"
    return path.read_text() if path.is_file() else ""
