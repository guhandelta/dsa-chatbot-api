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


def test_unclassified_uploads_use_explicit_all_language_scope():
    docs = uk.project('neutral', 'matrix-and-grid.md', 'A matrix is a rectangular grid of values.', 'custom')
    assert docs and all(d.metadata['language'] == uk.ALL_LANGUAGES for d in docs)


@pytest.mark.parametrize('filename', [
    'web-fundamentals-course-plan.pdf',
    'web-fundamentals-course-plan-revised.pdf',
    'Frontend REACT Developer.pdf',
])
def test_course_plans_are_not_learner_retrieval_sources(filename):
    docs = uk.project('course-plan', filename,
                      'A course plan lists goals, sequencing, and future modules.', 'custom')
    assert not docs


@pytest.mark.parametrize(('filename', 'language'), [
    ('PHP 8 notes.md', 'php'), ('Dart fundamentals.md', 'dart'),
    ('Kotlin basics.md', 'kotlin'), ('Swift foundations.md', 'swift'),
    ('Scala 3 guide.md', 'scala'), ('Haskell guide.md', 'haskell'),
    ('PHP8_DSA_CORPUS.md', 'php'), ('scala3-dsa-catalog.md', 'scala'),
    ('C17 memory.md', 'c'), ('C++ vectors.md', 'cpp'), ('C# collections.md', 'csharp'),
])
def test_infer_language_supports_all_currently_supported_languages(filename, language):
    assert uk.infer_language(filename) == language


def test_unlabeled_upload_uses_valid_language_from_frontmatter():
    text = ('---\nlanguage: kotlin\nsubject: kotlin\nverified: false\n---\n'
            'Kotlin nullable values require explicit handling before use.')
    docs = uk.project('kotlin-notes', 'nullable-values.md', text, 'custom')
    assert docs and all(d.metadata['language'] == 'kotlin' for d in docs)
    assert all(d.metadata['subject'] == 'kotlin' for d in docs)
    assert all('language: kotlin' not in d.page_content for d in docs)


def test_conflicting_upload_and_frontmatter_languages_are_withheld():
    text = ('---\nlanguage: kotlin\nsubject: kotlin\n---\n'
            'Java nullable values require explicit handling before use.')
    docs = uk.project('java-notes', 'notes.md', text, 'custom', 'java')
    assert not docs


def test_unknown_frontmatter_language_does_not_become_a_supported_scope():
    text = ('---\nlanguage: imaginary\n---\n'
            'General language-neutral notes about algorithmic complexity and arrays.')
    docs = uk.project('unknown-notes', 'notes.md', text, 'custom')
    assert docs and all(d.metadata['language'] == uk.ALL_LANGUAGES for d in docs)


def test_frontmatter_subject_is_preserved_without_exposing_frontmatter():
    text = ('---\nsubject: spring-boot\nframework: spring\nverified: false\n---\n'
            'Spring Boot configuration binds external properties to typed settings.')
    docs = uk.project('boot', 'spring-boot.md', text, 'custom', 'java')
    assert docs and all(d.metadata['subject'] == 'spring-boot' for d in docs)
    assert all(d.metadata['framework'] == 'spring' for d in docs)
    assert all('verified: false' not in d.page_content for d in docs)


async def test_language_neutral_upload_is_available_to_multiple_languages(db):
    user = User(email='neutral-owner@x.com', hashed_password='unused')
    db.add(user)
    await db.flush()
    db.add(KnowledgeDocument(owner_id=user.id, filename='matrix-and-grid.md', track='custom',
                             status='published', text='A matrix is a rectangular grid of values.'))
    await db.commit()
    assert await uk.search(db, 'matrix grid', 'dsa', 'java')
    assert await uk.search(db, 'matrix grid', 'dsa', 'javascript')


async def test_subject_scoped_uploads_require_exact_frontmatter_scope(db):
    user = User(email='subject-owner@x.com', hashed_password='unused')
    db.add(user)
    await db.flush()
    db.add_all([
        KnowledgeDocument(owner_id=user.id, filename='boot.md', track='custom', status='published',
            language='java', text='---\nsubject: spring-boot\n---\nSpring Boot configuration properties bind to typed settings.'),
        KnowledgeDocument(owner_id=user.id, filename='security.md', track='custom', status='published',
            language='java', text='---\nsubject: spring-security\n---\nSpring Security filter chains define request authorization.'),
        KnowledgeDocument(owner_id=user.id, filename='plain-java.md', track='custom', status='published',
            language='java', text='Java collections preserve equality and hash contracts.'),
    ])
    await db.commit()

    boot = await uk.search(db, 'configuration properties', 'language', 'java', subject='spring-boot')
    security = await uk.search(db, 'filter chains authorization', 'language', 'java', subject='spring-security')
    assert len(boot) == 1 and boot[0].metadata['subject'] == 'spring-boot'
    assert len(security) == 1 and security[0].metadata['subject'] == 'spring-security'
    assert not await uk.search(db, 'collections equality', 'language', 'java', subject='spring-boot')


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
