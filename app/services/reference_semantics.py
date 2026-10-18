"""Versioned semantic index for curated supplemental references.

The manifest is published only after a complete build. Model identity is explicit;
this collection never mixes vectors from the legacy unlabelled index.
"""
import json
from pathlib import Path
from functools import lru_cache
from threading import Lock

from app.core.config import settings
from app.services.reference_library import current_document

MANIFEST = Path(__file__).resolve().parents[2] / 'data/reference_library/semantic-index.json'
MODEL = 'models/gemini-embedding-001'
_STORE_LOCK = Lock()


def embeddings():
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    if not settings.google_api_key:
        raise RuntimeError('Google embedding key unavailable for labelled reference index')
    return GoogleGenerativeAIEmbeddings(model=MODEL, google_api_key=settings.google_api_key,
                                        request_options={'timeout':20})


@lru_cache(maxsize=2)
def _store(collection, model, directory):
    if model != MODEL:
        raise ValueError('Reference embedding model mismatch; rebuild index')
    from langchain_chroma import Chroma
    return Chroma(collection_name=collection,persist_directory=directory,embedding_function=embeddings())


def search(query, language, subject=None, k=4):
    if not MANIFEST.exists() or settings.vector_store != 'chroma':
        return []
    manifest=json.loads(MANIFEST.read_text())
    # lru_cache alone allows concurrent cold misses to execute its factory.
    # Chroma's shared client initialization must finish before another caller
    # tries to open the same persistent database.
    with _STORE_LOCK:
        store=_store(manifest['collection'],manifest['model'],settings.chroma_persist_dir)
    where={'$and':[{'language':language},{'subject':subject or language},{'contains_answer':False}]}
    results=store.similarity_search(query,k=k,filter=where)
    # Current curation always overrides persisted vector text and metadata.
    out=[]
    for result in results:
        doc=current_document(result)
        if doc and doc.metadata.get('language')==language and doc.metadata.get('subject')==(subject or language):
            out.append(doc)
    return out


def balanced_results(*rankings):
    """Round-robin unique sources: no retrieval channel consumes every slot."""
    seen=set()
    for rank in range(max((len(r) for r in rankings),default=0)):
        for ranking in rankings:
            if rank >= len(ranking):continue
            doc=ranking[rank]
            key=doc.page_content
            if key not in seen:
                seen.add(key)
                yield doc
