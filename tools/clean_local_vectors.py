"""Remove obsolete/unsafe local Chroma copies without creating embeddings.

Current curated files and approved SQL projections remain authoritative. The
existing lexical retrievers work without re-embedding. This command never
initializes an embedding provider or touches a remote vector store.
"""
import asyncio
from collections import Counter
import json
from pathlib import Path
import shutil

from app.core.config import settings

API = Path(__file__).resolve().parents[1]
OUTPUT = API.parent / 'reports/knowledge-base-cleanup-2026-10-17'


async def main():
    if settings.vector_store != 'chroma':
        raise RuntimeError('Local Chroma cleanup only; remote indexes require their own reconciliation.')
    source = Path(settings.chroma_persist_dir)
    if not source.is_absolute():
        source = API / source
    if not (source / 'chroma.sqlite3').is_file():
        print('No existing Chroma store. Nothing to clean.')
        return
    backup = OUTPUT / 'backup/chroma_db'
    if not backup.exists():
        shutil.copytree(source, backup)
        backup.chmod(0o700)

    import chromadb
    from chromadb.config import Settings
    from langchain_core.documents import Document
    from app.services.reference_library import current_document

    client = chromadb.PersistentClient(path=str(source), settings=Settings(anonymized_telemetry=False))
    collection = client.get_collection('dsa_problems', embedding_function=None)
    before = collection.count()
    snapshot = collection.get(include=['metadatas', 'documents'])
    removed, reasons = [], Counter()
    from app.db.database import SessionLocal
    from app.db.models import KnowledgeDocument
    from app.services.knowledge_hygiene import source_is_plan
    from app.services.uploaded_knowledge import project
    from sqlalchemy import select
    async with SessionLocal() as session:
        rows = list((await session.scalars(select(KnowledgeDocument))).all())
        # Withdraw authoring plans rather than leaving an old API process able
        # to consume their previously approved SQL projection.
        withdrawn = []
        for row in rows:
            if row.status == 'published' and source_is_plan(row.filename):
                withdrawn.append({'document_id': row.id, 'filename': row.filename, 'before_status': row.status})
                row.status = 'rejected'
                row.review_note = 'Local knowledge-base cleanup: authoring plan; preserved for staff, withdrawn from learner references.'
        allowed = {(c.metadata['document_id'], c.metadata['revision'], c.page_content)
                   for row in rows if row.status == 'published'
                   for c in project(row.id, row.filename, row.text, row.track, row.language)}
        for rid, meta, text in zip(snapshot['ids'], snapshot['metadatas'], snapshot['documents']):
            meta = meta or {}
            reason = None
            if meta.get('contains_answer') is not False:
                reason = 'Missing or unsafe answer flag on legacy vector.'
            elif str(meta.get('problem_id', '')).startswith('upload:') or meta.get('document_id'):
                key = (meta.get('document_id'), meta.get('revision'), text)
                if key not in allowed:
                    reason = 'Obsolete, withdrawn or unmatched uploaded projection.'
            else:
                current = current_document(Document(page_content=text or '', metadata=meta))
                if current is None or current.page_content != text:
                    reason = 'Removed, duplicate or outdated packaged reference.'
            if reason:
                removed.append(rid)
                reasons[reason] += 1
        for start in range(0, len(removed), 500):
            collection.delete(ids=removed[start:start+500])
        removed_set = set(removed)
        for row in rows:
            prior = json.loads(row.chunk_ids or '[]')
            current = [rid for rid in prior if rid not in removed_set]
            if current != prior:
                row.chunk_ids = json.dumps(current)
        await session.commit()
    after = collection.count()
    report = {'before': before, 'after': after, 'removed_count': len(removed),
              'reasons': dict(reasons), 'withdrawn_planning_uploads': withdrawn,
              'deleted_vector_ids': removed,
              'embedding_calls': 0,
              'note': 'Current SQL and packaged lexical retrieval remain available. Physical embeddings were not regenerated.'}
    path = OUTPUT / 'vector-cleanup.json'
    if path.exists():
        path = OUTPUT / 'latest-vector-cleanup.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('before', 'after', 'removed_count', 'reasons', 'embedding_calls')}, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
