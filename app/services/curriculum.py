"""Canonical release corpus. Original answers stay out of learner retrieval."""
import json
from functools import lru_cache
from pathlib import Path

CORPUS_PATH = Path(__file__).resolve().parents[2] / "data" / "curriculum" / "java-javascript.jsonl"
RELEASE_LANGUAGES = ("javascript", "java")


@lru_cache(maxsize=1)
def records() -> list[dict]:
    rows = [json.loads(line) for line in CORPUS_PATH.open(encoding="utf-8") if line.strip()]
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate curriculum IDs")
    return rows


def concept_items() -> list[dict]:
    return [r for r in records() if r["metadata"]["kind"] == "concept"
            and r["metadata"]["language"] in RELEASE_LANGUAGES]


def concept_document(content_id: str) -> str:
    return next((r["document"] for r in concept_items() if "corpus-" + r["id"] == content_id), "")


def retrieval_documents():
    from langchain_core.documents import Document
    # Only explicit answer-free records are eligible. Exercise/gotcha answers
    # are preserved in the canonical file but never indexed into learner chat.
    for r in records():
        m = r["metadata"]
        if m.get("contains_answer") is not False or m.get("kind") in ("exercise", "gotcha"):
            continue
        if m.get("language") not in RELEASE_LANGUAGES:
            continue
        yield Document(page_content=r["document"], metadata={
            **m, "track": "language", "problem_id": "corpus-" + r["id"],
            "contains_answer": False, "corpus_version": "java-javascript-v1",
        })
