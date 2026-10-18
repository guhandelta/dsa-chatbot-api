"""Supplemental RAG references, separate from verified executable curricula."""
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path

LIBRARY_DIR = Path(__file__).resolve().parents[2] / 'data' / 'reference_library'


def version():
    path = LIBRARY_DIR / 'records.jsonl'
    if not path.exists():
        return (str(path), 0, 0)
    stat = path.stat()
    return (str(path), stat.st_mtime_ns, stat.st_size)


def records():
    return _records(*version())


@lru_cache(maxsize=1)
def _records(path, modified, size):
    if not modified:
        return []
    path = Path(path)
    rows = [json.loads(line) for line in path.open(encoding='utf-8') if line.strip()]
    ids = [r['id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate reference library IDs')
    return rows


def subjects():
    return _subjects(version())


@lru_cache(maxsize=1)
def _subjects(library_version):
    counts = Counter(r['metadata']['subject'] for r in records())
    safe = Counter(r['metadata']['subject'] for r in records() if eligible(r))
    languages = {r['metadata']['subject']:r['metadata']['language'] for r in records()}
    return [{'id':s, 'language':languages[s], 'records':n, 'retrievable_records':safe[s],
             'status':'reference_only', 'executable':False} for s,n in sorted(counts.items())]


def eligible(row):
    from app.services.knowledge_hygiene import quarantine_reason, PUBLIC_REFERENCE_KINDS
    m = row['metadata']
    return (m.get('contains_answer') is False and m.get('kind') in PUBLIC_REFERENCE_KINDS
            and bool(row['document'].strip()) and not quarantine_reason(row))


def current_document(document):
    """Replace stale reference vectors with current curated content, or drop them.

    Re-embedding is unnecessary for enforcing removals/corrections. Ranking can
    still be stale until the vector index is refreshed, so local search remains
    available alongside it.
    """
    meta = document.metadata
    rid = str(meta.get('problem_id', ''))
    if not rid.startswith('ref-') and meta.get('source') != 'reference-library':
        if rid.startswith('corpus-'):
            from app.services.curriculum import records
            from app.services.knowledge_hygiene import PUBLIC_REFERENCE_KINDS
            row = next((r for r in records() if 'corpus-' + r['id'] == rid), None)
            if not row or row['metadata'].get('contains_answer') is not False or row['metadata'].get('kind') not in PUBLIC_REFERENCE_KINDS:
                return None
            from langchain_core.documents import Document
            return Document(page_content=row['document'], metadata={
                **row['metadata'], 'problem_id': rid, 'track': 'language'})
        if meta.get('catalog') == 'release-v1':
            from app.services.content_catalog import find_path
            from app.services.content_access import public_text
            import re
            path = find_path(rid)
            if not path:
                return None
            current = re.sub(r'\s+', ' ', public_text(path.read_text())).strip()
            old_chunk = re.sub(r'\s+', ' ', document.page_content).strip()
            if not old_chunk or old_chunk not in current:
                return None
        return document
    current = _by_id(version()).get(rid)
    if current is None or not eligible(current):
        return None
    from langchain_core.documents import Document
    return Document(page_content=current['document'], metadata={
        **current['metadata'], 'problem_id': current['id']})


@lru_cache(maxsize=1)
def _by_id(library_version):
    out = {}
    for row in records():
        out[row['id']] = row
        for alias in row.get('duplicate_ids', []) + row.get('previous_ids', []):
            out[alias] = row
    return out


def documents(language, subject=None):
    from langchain_core.documents import Document
    # Framework and embedded references require explicit subject selection.
    scope = subject or language
    for r in records():
        m = r['metadata']
        if m['language'] == language and m['subject'] == scope and eligible(r):
            yield Document(page_content=r['document'], metadata={**m,'problem_id':r['id']})
