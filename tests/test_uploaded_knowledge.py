"""Upload safety/lifecycle tests independent of paid embeddings and model output."""
from types import SimpleNamespace

import pytest
from sqlalchemy import select

from app.db.models import KnowledgeDocument, User, VectorCleanupJob
from app.services import rag_pipeline, uploaded_knowledge as uk
from tests.test_learn import admin, store, _upload_text  # shared approval/fake-store fixtures


@pytest.mark.parametrize('heading', ['## Solutions', 'Answer key', '4. Gotcha catalogue',
    'Exercise formats', 'Snippet Result Why', 'expected_output: 42', '2. Index handling'])
def test_answer_boundary_withholds_rest(heading):
    assert uk.reference_text('Arrays use numeric indices.\n' + heading + '\nSECRET ANSWER') == 'Arrays use numeric indices.'


def test_code_and_structured_payloads_are_withheld():
    view = uk.reference_text('Reference notes\n```java\nreturn SECRET;\n```\nArrays have fixed length.\nid: hidden\nSECRET')
    assert view == 'Reference notes\nArrays have fixed length.'
    assert uk.infer_language('JavaScript arrays.pdf') == 'javascript'
    assert uk.infer_language('Java arrays.pdf') == 'java'
    assert uk.infer_language('Java and Python.pdf') is None
    assert uk.infer_language('unscoped.pdf') is None


async def test_approved_live_projection_scopes_and_preserves_review(client, admin, store, db):
    result = await _upload_text(client, admin, filename='Java arrays.pdf', track='language',
        text='Java arrays have fixed capacity.\n## Answers\nSECRET')
    doc_id = result.json()['document_id']
    original = await db.get(KnowledgeDocument, doc_id)
    reviewed_at = original.reviewed_at
    docs = await uk.search(db, 'arrays capacity', 'language', 'java')
    assert len(docs) == 1
    assert docs[0].metadata['document_id'] == doc_id
    assert docs[0].metadata['contains_answer'] is False
    assert docs[0].metadata['verified'] is False
    assert 'SECRET' not in docs[0].page_content
    assert not await uk.search(db, 'arrays', 'language', 'javascript')
    assert not await uk.search(db, 'arrays', 'dsa', 'java')
    assert not await uk.search(db, 'arrays', 'language', 'java', focus_id='two-sum')
    assert not await uk.search(db, 'arrays', 'language', 'java', subject='spring-boot')
    await db.refresh(original)
    assert original.reviewed_at == reviewed_at and original.text.endswith('SECRET')
    assert store.docs and all('SECRET' not in d.page_content for d in store.docs.values())


async def test_failed_vector_deletion_queues_retry_and_immediately_revokes_access(client, admin, store, db):
    r = await _upload_text(client, admin, filename='Java arrays.md', text='Java arrays store values.')
    doc_id = r.json()['document_id']
    assert await uk.search(db, 'arrays', 'dsa', 'java')
    store.fail_delete = True
    assert (await client.post(f'/learn/documents/{doc_id}/reject', headers=admin)).status_code == 200
    db.expire_all()
    assert not await uk.search(db, 'arrays', 'dsa', 'java')
    job = await db.scalar(select(VectorCleanupJob))
    assert job.attempts == 1 and job.last_error == 'RuntimeError'
    assert store.docs  # stale external state exists, yet cannot reach retrieval
    from app.services.maintenance import drain_cleanup
    store.fail_delete = False
    assert await drain_cleanup(db) == 1
    assert not store.docs and await db.scalar(select(VectorCleanupJob)) is None


async def test_stale_upload_vectors_are_dropped_and_safe_excerpt_is_returned(monkeypatch):
    captured = []
    class LLM:
        async def ainvoke(self, messages):
            captured.extend(messages)
            return SimpleNamespace(content='Guidance')
    class Store:
        def similarity_search(self, *a, **kw):
            return [SimpleNamespace(page_content='STALE ANSWER', metadata={'problem_id':'upload:deleted', 'contains_answer':False})]
    monkeypatch.setattr(rag_pipeline, 'get_llm', lambda _: LLM())
    monkeypatch.setattr(rag_pipeline, 'get_vectorstore', lambda: Store())
    monkeypatch.setattr('app.services.curriculum_search.search', lambda *a, **kw: [])
    citations = []
    docs = list(uk.project('live', 'Java arrays.pdf', 'Java arrays have fixed capacity.', 'language'))
    await rag_pipeline.run_rag_chat('arrays', 'openai', [], 'java', 'language', uploaded_documents=docs, citations=citations)
    assert 'STALE ANSWER' not in captured[0].content
    assert 'fixed capacity' in captured[0].content
    assert citations[0]['filename'] == 'Java arrays.pdf' and len(citations[0]['revision']) == 64


async def test_pending_and_deleted_documents_never_retrieve(db):
    user = User(email='upload-owner@x.com', hashed_password='unused')
    db.add(user)
    await db.flush()
    doc = KnowledgeDocument(owner_id=user.id, filename='Java arrays.pdf', track='language', status='pending', text='Java arrays are fixed length.')
    db.add(doc)
    await db.commit()
    assert not await uk.search(db, 'arrays', 'language', 'java')
    doc.status = 'published'
    await db.commit()
    assert await uk.search(db, 'arrays', 'language', 'java')
    await db.delete(doc)
    await db.commit()
    assert not await uk.search(db, 'arrays', 'language', 'java')


async def test_partial_index_failure_preserves_old_approval_and_queues_all_new_ids(client, admin, store, db, monkeypatch):
    result = await _upload_text(client, admin, filename='Java arrays.md', text='Java arrays original approved notes.')
    doc_id = result.json()['document_id']
    doc = await db.get(KnowledgeDocument,doc_id)
    approved_at, original_text = doc.reviewed_at, doc.text
    old_ids = set(store.docs)
    original_add = store.add_documents
    def partial(docs, ids=None):
        original_add(docs[:1], ids=ids[:1])
        raise RuntimeError('provider failed after writing a chunk')
    monkeypatch.setattr(store,'add_documents',partial)
    failed = await _upload_text(client,admin,filename='Java arrays.md',text='Java arrays replacement notes.')
    assert failed.status_code == 502
    db.expire_all()
    preserved = await db.get(KnowledgeDocument,doc_id)
    assert preserved.text == original_text and preserved.reviewed_at == approved_at and preserved.status=='published'
    from app.services.maintenance import drain_cleanup
    assert await db.scalar(select(VectorCleanupJob)) is not None
    await drain_cleanup(db)
    assert set(store.docs) == old_ids


async def test_explicit_language_restores_pasted_notes_without_filename_guessing(client, admin, store, db):
    result = await client.post('/learn/train',headers=admin,json={
        'filename':'notes.md','text':'Arrays have fixed length.','language':'java','track':'language'})
    assert result.status_code == 200, result.text
    assert result.json()['retrieval_status'] == 'available'
    assert result.json()['reference_language'] == 'java'
    assert await uk.search(db,'arrays','language','java')
    assert not await uk.search(db,'arrays','language','javascript')
    invalid = await client.post('/learn/train',headers=admin,json={'text':'Some notes','language':'not-real'})
    assert invalid.status_code == 422


async def test_explicit_language_cannot_silently_mislabel_named_source(client, admin, store):
    result = await client.post('/learn/train',headers=admin,json={
        'filename':'Java arrays.pdf','language':'javascript','text':'Arrays are fixed length.'})
    assert result.status_code == 422 and 'conflicts' in result.json()['detail']
    assert not store.docs
