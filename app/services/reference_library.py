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
    m = row['metadata']
    return (m.get('contains_answer') is False and m.get('kind') in ('concept','reference','curriculum','lens','exercise_format')
            and bool(row['document'].strip()))


def documents(language, subject=None):
    from langchain_core.documents import Document
    # Framework and embedded references require explicit subject selection.
    scope = subject or language
    for r in records():
        m = r['metadata']
        if m['language'] == language and m['subject'] == scope and eligible(r):
            yield Document(page_content=r['document'], metadata={**m,'problem_id':r['id']})
