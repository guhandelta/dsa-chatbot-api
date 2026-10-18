"""Local BM25 retrieval over the same approved, answer-safe release corpus.

Provides useful scoped retrieval before embeddings have been built, and when
an embedding provider is unavailable. It never broadens language or focus.
"""
import math
import re
from collections import Counter
from functools import lru_cache

from app.services.content_catalog import filter_content
from app.services.content_access import learner_document
from app.services.curriculum import retrieval_documents


def tokens(text: str) -> list[str]:
    # Split camelCase so a query such as "default value" matches getOrDefault.
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    return re.findall(r"[a-z0-9_]+", text.lower())


@lru_cache(maxsize=32)
def _index(track: str, language: str, focus_id: str | None, subject: str | None = None, library_version=None):
    from langchain_core.documents import Document
    tracks = {"dsa", "algorithm"} if track == "dsa" else {track}
    docs = []
    for c in ([] if subject else filter_content(language=language)):
        if c.source == "curriculum" or c.track not in tracks or (focus_id and c.id != focus_id):
            continue
        text = learner_document(c.id)
        # Preserve headings and code blocks in each locally retrieved section.
        sections = [text] if focus_id else re.split(r"(?=^## )", text, flags=re.M)
        for section in sections:
            if section.strip():
                docs.append(Document(page_content=section, metadata={
                    "problem_id": c.id, "track": c.track, "language": c.language or language,
                    "contains_answer": False, "source": c.id,
                }))
    if track == "language" and not subject:
        docs.extend(d for d in retrieval_documents()
                    if d.metadata["language"] == language
                    and (not focus_id or d.metadata["problem_id"] == focus_id))
    if track == "language" and not focus_id:
        from app.services.reference_library import documents
        docs.extend(documents(language, subject))
    counts = [Counter(tokens(d.page_content)) for d in docs]
    frequencies = Counter(t for c in counts for t in c)
    avg_length = sum(sum(c.values()) for c in counts) / max(len(counts), 1)
    return docs, counts, frequencies, avg_length


def search(query: str, track: str, language: str, focus_id: str | None = None, k: int = 4, subject: str | None = None):
    from app.services.reference_library import version
    from app.services.curriculum import version as curriculum_version
    docs, counts, frequencies, avg = _index(track, language, focus_id, subject, (version(), curriculum_version()))
    terms = set(tokens(query))
    ranked = []
    for i, c in enumerate(counts):
        length = sum(c.values())
        score = 0.0
        for term in terms & c.keys():
            frequency = c[term]
            idf = math.log(1 + (len(docs) - frequencies[term] + 0.5) / (frequencies[term] + 0.5))
            score += idf * frequency * 2.5 / (frequency + 1.5 * (0.25 + 0.75 * length / max(avg,1)))
        if score > 0 or focus_id:
            ranked.append((score, i))
    return [docs[i] for _, i in sorted(ranked, key=lambda x: (-x[0], x[1]))[:k]]
