"""Learner-safe content views and persisted, language-scoped solution access."""
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LearningEvent
from app.services.content_catalog import read_content

PROTECTED = re.compile(
    r"^##\s+(?:Approach|Hints|Thinking Style|Edge Cases|Common Mistakes|Solutions|"
    r"Interview Follow-ups|Answer|Reference Solution)\b", re.I | re.M
)


def public_text(markdown: str) -> str:
    # Front matter contains hidden tests and must never reach the learner.
    markdown = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", markdown, count=1, flags=re.S)
    match = PROTECTED.search(markdown)
    return markdown[:match.start()].rstrip() if match else markdown


LANGUAGE_ALIASES = {"js": "javascript", "ts": "typescript", "py": "python",
                    "c++": "cpp", "c#": "csharp", "cs": "csharp", "rb": "ruby",
                    "golang": "go"}
CODE_LANGUAGES = {"python", "javascript", "java", "typescript", "cpp", "c",
                  "rust", "ruby", "go", "csharp", "html", "css", "scss"}


def scoped_markdown(markdown: str, language: str) -> str:
    """Keep shared prose, but only the selected language's example sections/fences."""
    def canonical(label):
        key = label.strip().lower()
        return LANGUAGE_ALIASES.get(key, key)
    # Shared algorithm articles have per-language subsections, not just fences.
    sections = re.split(r"(?=^#{2,6} +)", markdown, flags=re.M)
    kept, skip_depth = [], None
    for section in sections:
        heading = re.match(r"^(#{2,6}) +([^\n]+)", section)
        if heading:
            depth, label = len(heading[1]), canonical(heading[2])
            if skip_depth is not None and depth <= skip_depth:
                skip_depth = None
            if label in CODE_LANGUAGES and label != language:
                skip_depth = depth
        if skip_depth is None:
            kept.append(section)
    def fence(match):
        label = canonical(match[1])
        return "" if label in CODE_LANGUAGES and label != language else match[0]
    return re.sub(r"^```([^\s`]*)[^\n]*\n.*?^```[ \t]*$", fence,
                  "".join(kept), flags=re.M | re.S).strip()


def learner_document(content_id: str, language: str | None = None) -> str:
    text = public_text(read_content(content_id))
    return scoped_markdown(text, language) if language else text


def solution_document(content_id: str, language: str) -> str:
    body = read_content(content_id)
    labels = {"javascript": "JavaScript", "java": "Java", "python": "Python",
              "cpp": "C++", "c": "C", "rust": "Rust", "typescript": "TypeScript",
              "ruby": "Ruby", "go": "Go", "csharp": "C#"}
    label = labels.get(language)
    if not label:
        return ""
    # Only the requested language is returned. Never send every solution to the UI.
    match = re.search(rf"^### {re.escape(label)}\s*\n(.*?)(?=^### |^## |\Z)", body, re.S | re.M)
    if not match:
        return ""
    approach = re.search(r"^## Approach\s*\n(.*?)(?=^## |\Z)", body, re.S | re.M)
    return (f"## Approach\n{approach.group(1).strip()}\n\n" if approach else "") + f"## {label} solution\n{match.group(1).strip()}"


def evaluation_completed(evidence: dict, language: str) -> bool:
    results = (evidence.get("curated") or {}).get("results", [])
    return any(r.get("language") == language and r.get("tier") == 1
               and r.get("status") in ("passed", "failed")
               and r.get("total_cases", 0) > 0 for r in results)


def reveal_policy() -> dict:
    """The configured reveal rule, phrased for the learner. Which rule to use
    is an open product decision, so it lives in settings, not in code."""
    from app.core.config import settings
    policy, minimum = settings.solution_reveal_policy, settings.solution_reveal_min_evaluations
    requirement = {
        "after_evaluation": ("Complete an evaluation to unlock the reference solution." if minimum == 1 else
                             f"Complete {minimum} evaluations to unlock the reference solution."),
        "after_pass": "Pass every test in an evaluation to unlock the reference solution.",
        "disabled": "Reference solutions are not available in this course.",
    }[policy]
    return {"policy": policy, "min_evaluations": minimum, "requirement": requirement}


async def can_reveal(session: AsyncSession, user_id: str, content_id: str, language: str) -> bool:
    """Evaluation always comes first: test runs and reviews never unlock a
    solution on their own. The remaining rule comes from reveal_policy()."""
    from sqlalchemy import func
    from app.core.config import settings
    policy = settings.solution_reveal_policy
    if policy == "disabled":
        return False
    scope = (LearningEvent.user_id == user_id, LearningEvent.problem_id == content_id,
             LearningEvent.language == language)
    evaluated = await session.scalar(select(func.count()).select_from(LearningEvent).where(
        *scope, LearningEvent.kind == "evaluated"))
    if policy == "after_pass":
        solved = await session.scalar(select(LearningEvent.id).where(*scope, LearningEvent.kind == "solved").limit(1))
        return bool(evaluated) and solved is not None
    return evaluated >= settings.solution_reveal_min_evaluations
