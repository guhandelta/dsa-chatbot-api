"""Canonical teaching routes retain role boundaries and shared review state."""
import pytest
from sqlalchemy import select

from app.db.models import KnowledgeDocument
from tests.test_language_access import account
from tests.test_learn import admin, instructor, store  # noqa: F401


@pytest.mark.parametrize('prefix', ['/teach', '/learn'])
@pytest.mark.parametrize('method,path', [
    ('get', '/status'), ('get', '/documents'), ('post', '/train'),
    ('get', '/documents/missing'), ('delete', '/documents/missing'),
    ('post', '/documents/missing/approve'), ('post', '/documents/missing/reject'),
])
async def test_teaching_requires_authentication(client, prefix, method, path):
    response = await client.request(method, prefix + path)
    assert response.status_code == 401, response.text


@pytest.mark.parametrize('role', ['student', 'instructor', 'admin'])
@pytest.mark.parametrize('suspended', [False, True])
async def test_status_documents_and_upload_require_active_staff(client, db, store, role, suspended):
    user, headers = await account(db, role=role)
    if suspended:
        user.status = 'suspended'
        await db.commit()
    permitted = role != 'student' and not suspended
    for prefix in ('/teach', '/learn'):
        for path in ('/status', '/documents'):
            response = await client.get(prefix + path, headers=headers)
            assert response.status_code == (200 if permitted else 403), response.text
        if not permitted:
            response = await client.post(prefix + '/train', headers=headers,
                                         json={'text': '# Trees\nTrees have nodes.', 'filename': 'trees.md'})
            assert response.status_code == 403, response.text
    if not permitted:
        assert (await db.scalars(select(KnowledgeDocument))).all() == []
        assert store.docs == {}


async def test_canonical_upload_and_legacy_review_share_pending_lifecycle(client, instructor, admin, store):
    response = await client.post('/teach/train', headers=instructor,
                                 json={'filename': 'trees.md', 'text': '# Trees\nTrees have nodes.', 'track': 'DSA'})
    assert response.status_code == 200, response.text
    uploaded = response.json()
    assert uploaded['review_status'] == 'pending'
    assert uploaded['chunks_trained'] == 0
    assert uploaded['track'] == 'dsa'
    assert store.docs == {}
    doc_id = uploaded['document_id']
    for prefix in ('/teach', '/learn'):
        status = await client.get(prefix + '/status', headers=instructor)
        assert status.json()['requires_review'] is True
        listing = await client.get(prefix + '/documents?status=pending', headers=admin)
        assert [doc['id'] for doc in listing.json()] == [doc_id]
        for action in ('approve', 'reject'):
            denied = await client.post(f'{prefix}/documents/{doc_id}/{action}', headers=instructor)
            assert denied.status_code == 403
    assert store.docs == {}
    approved = await client.post(f'/learn/documents/{doc_id}/approve', headers=admin)
    assert approved.status_code == 200, approved.text
    assert approved.json()['status'] == 'published'
    assert approved.json()['chunks'] == len(store.docs) > 0
    detail = await client.get(f'/teach/documents/{doc_id}', headers=instructor)
    assert detail.json()['status'] == 'published'
    assert 'Trees have nodes.' in detail.json()['preview']
    assert (await client.post(f'/teach/documents/{doc_id}/approve', headers=admin)).status_code == 409


async def test_canonical_documents_are_owner_scoped(client, db, instructor, admin, store):
    _, stranger = await account(db, role='instructor')
    response = await client.post('/teach/train', headers=instructor, json={'text': 'Private teaching notes'})
    doc_id = response.json()['document_id']
    assert (await client.get('/teach/documents', headers=stranger)).json() == []
    for method in ('get', 'delete'):
        assert (await client.request(method, f'/teach/documents/{doc_id}', headers=stranger)).status_code == 404
    assert (await client.get(f'/teach/documents/{doc_id}', headers=admin)).status_code == 200


async def test_openapi_exposes_teach_and_hides_legacy_alias(client):
    response = await client.get('/openapi.json')
    assert response.status_code == 200
    paths = response.json()['paths']
    assert {'/teach/status', '/teach/train', '/teach/documents',
            '/teach/documents/{doc_id}/approve'} <= paths.keys()
    assert not any(path.startswith('/learn/') for path in paths)


async def test_canonical_admin_multipart_upload_publishes_and_legacy_can_read(client, admin, store):
    response = await client.post('/teach/train', headers=admin,
                                 files={'file': ('notes.md', b'# Queues\nFirst in, first out.', 'text/markdown')},
                                 data={'track': 'dsa'})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body['review_status'] == 'published'
    assert body['chunks_trained'] == len(store.docs) > 0
    assert (await client.get('/teach/status', headers=admin)).json()['requires_review'] is False
    detail = await client.get('/learn/documents/' + body['document_id'], headers=admin)
    assert detail.status_code == 200, detail.text
    assert detail.json()['preview'] == '# Queues\nFirst in, first out.'
    assert detail.json()['status'] == 'published'
