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


def learner_document(content_id: str) -> str:
    return public_text(read_content(content_id))


def solution_document(content_id: str, language: str) -> str:
    body = read_content(content_id)
    labels = {"javascript": "JavaScript", "java": "Java", "python": "Python",
              "cpp": "C++", "c": "C", "rust": "Rust"}
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


async def can_reveal(session: AsyncSession, user_id: str, content_id: str, language: str) -> bool:
    event = await session.scalar(select(LearningEvent.id).where(
        LearningEvent.user_id == user_id,
        LearningEvent.problem_id == content_id,
        LearningEvent.language == language,
        LearningEvent.kind == "evaluated",
    ).limit(1))
    return event is not None
