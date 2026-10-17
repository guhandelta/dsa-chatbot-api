"""Approved uploads, projected afresh rather than trusting stale vector metadata.

This is a conservative reference view, not an assertion that arbitrary prose is
answer-free. Code, assessment tables, and everything after an answer/exercise
boundary are withheld. Original text and approval evidence are never changed.
"""
import asyncio
import hashlib
import re
from functools import lru_cache

from langchain_core.documents import Document
from sqlalchemy import or_, select

from app.db.models import KnowledgeDocument

PROJECTION_VERSION = "upload-reference-v1"
_LANGUAGES = (("javascript", r"javascript|\bjs\b"), ("typescript", r"typescript|\bts\b"),
              ("java", r"\bjava\b"), ("python", r"python"), ("rust", r"\brust\b"),
              ("cpp", r"c\+\+|\bcpp\b"), ("go", r"\bgolang\b|\bgo\b"))
# Stop, rather than merely removing a heading: PDF tables can continue many
# pages after the heading and extraction can interleave columns/page furniture.
_BOUNDARY = re.compile(r"^\s*(?:#{1,6}\s*|\d+[.)]\s*)?(?:gotcha|curriculum levels|exercise|workout|quiz|solution|answer|canonical|reference implementation|ready.to.ingest|chunk schema|ingestion checklist|snippet\s+result|example_good|expected(?:_output)?\s*:|test_cases\s*:)", re.I)
_CODE = re.compile(r"(?:[{};]|=>|^\s*(?:def |class |import |from \S+ import |return |public |static |function |const |let |var |for\s*\(|while\s*\())")


def infer_language(filename: str) -> str | None:
    # JS contains the word Java as a prefix; remove it before matching Java.
    lowered = filename.lower()
    if re.search(_LANGUAGES[0][1], lowered):
        return "javascript"
    if re.search(_LANGUAGES[1][1], lowered):
        return "typescript"
    found = [lang for lang, pattern in _LANGUAGES[2:] if re.search(pattern, lowered)]
    return found[0] if len(found) == 1 else None


def reference_text(text: str) -> str:
    from app.services.content_access import public_text
    lines = []
    fenced = False
    for line in public_text(text).splitlines():
        if _BOUNDARY.search(line):
            break
        # Numbered training blueprints contain implementations from section 2.
        if re.match(r"^\s*(?:#{1,6}\s*)?[2-9]\d*[.)]\s+", line):
            break
        if line.strip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if fenced or _CODE.search(line):
            continue
        # No free-form code/structured payload blocks from linking-chunk exports.
        if re.match(r"^\s*(?:id|kind|language|tags|example\w*|answer\w*|solution\w*)\s*:", line, re.I):
            break
        lines.append(line)
    return "\n".join(lines).strip()


@lru_cache(maxsize=256)
def project(doc_id: str, filename: str, text: str, track: str, explicit_language: str = "") -> tuple[Document, ...]:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    language = explicit_language or infer_language(filename) or "und"
    safe = reference_text(text)
    if not safe:
        return ()  # ambiguous language requires instructor clarification
    revision = hashlib.sha256((PROJECTION_VERSION + text + filename + track + language).encode()).hexdigest()
    meta = {"problem_id": "upload:" + doc_id, "document_id": doc_id,
            "source": filename, "track": track, "language": language,
            "contains_answer": False, "kind": "reference", "revision": revision,
            "projection_version": PROJECTION_VERSION, "verified": False}
    return tuple(RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=120).create_documents([safe], metadatas=[meta]))


async def search(session, query: str, track: str, language: str, focus_id=None, subject=None, *, max_documents=None) -> list[Document]:
    if focus_id or subject:
        return []
    tracks = ["dsa", "algorithm", "custom"] if track == "dsa" else [track, "custom"]
    stmt=select(KnowledgeDocument).where(KnowledgeDocument.status=="published",KnowledgeDocument.track.in_(tracks))
    if max_documents is not None:
        if not 1 <= max_documents <= 100:
            raise ValueError("Invalid upload search limit")
        stmt=stmt.where(or_(KnowledgeDocument.language==language,KnowledgeDocument.language==""))
        stmt=stmt.order_by(KnowledgeDocument.created_at.desc()).limit(max_documents)
    rows=(await session.scalars(stmt)).all()
    snapshots=[(r.id,r.filename,r.text,r.track,r.language) for r in rows]
    return await asyncio.to_thread(_rank, snapshots, query, language)


def _rank(rows, query, language):
    docs = [chunk for row in rows for chunk in project(*row)
            if chunk.metadata["language"] == language]
    if not docs:
        return []
    # Lexical retrieval avoids paid re-embedding of legacy material and applies
    # exactly the same projection as new vector indexing.
    stopwords = {"a", "an", "the", "is", "are", "of", "to", "in", "and", "or", "how", "what", "why", "can", "i", "me", "explain", "does", "do", "for", "with"}
    terms = set(re.findall(r"\w+", query.lower())) - stopwords
    if not terms:
        return []
    scored = [(len(terms & set(re.findall(r"\w+", d.page_content.lower()))) +
               2 * len(terms & set(re.findall(r"\w+", d.metadata["source"].lower()))), i, d)
              for i, d in enumerate(docs)]
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [d for score, _, d in scored[:4] if score > 0]
