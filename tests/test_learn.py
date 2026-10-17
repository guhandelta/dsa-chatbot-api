# /learn: knowledge-base uploads with admin review.
# The vector store is replaced by an in-memory fake — these check role
# gating, validation, the pending → published/rejected lifecycle, and that
# vectors are written and removed exactly when they should be.
import json

import pytest
from sqlalchemy import select, update

from app.core.config import settings
from app.db.models import KnowledgeDocument, User
from app.routers import learn as learn_router
from app.services import knowledge_base


class FakeStore:
    """Records what would have been embedded or deleted."""

    def __init__(self):
        self.docs: dict[str, object] = {}
        self.deleted: list[str] = []
        self.fail_add = False
        self.fail_delete = False
        self._n = 0

    def add_documents(self, docs, ids=None):
        if self.fail_add:
            raise RuntimeError("embedding provider down")
        result = []
        for index, d in enumerate(docs):
            self._n += 1
            result.append(ids[index] if ids is not None else f"v{self._n}")
            self.docs[result[-1]] = d
        return result

    def delete(self, ids=None, **_):
        if self.fail_delete:
            raise RuntimeError("store unavailable")
        for i in ids or []:
            self.deleted.append(i)
            self.docs.pop(i, None)


@pytest.fixture
def store(monkeypatch):
    s = FakeStore()
    monkeypatch.setattr(knowledge_base, "get_vectorstore", lambda: s)
    return s


async def _reg(client, email):
    r = await client.post("/auth/register", json={"email": email, "password": "password123"})
    body = r.json()
    return {"Authorization": f"Bearer {body['access_token']}"}, body["user"]["id"]


@pytest.fixture
async def admin(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_emails", "kb-admin@x.com")
    h, _ = await _reg(client, "kb-admin@x.com")
    return h


async def _make_instructor(client, db, email):
    h, uid = await _reg(client, email)
    await db.execute(update(User).where(User.id == uid).values(role="instructor"))
    await db.commit()
    return h


@pytest.fixture
async def instructor(client, db):
    return await _make_instructor(client, db, "kb-instructor@x.com")


async def _upload_text(client, headers, text="## Heaps\nA heap is a tree.", filename="heaps.md", track="dsa"):
    return await client.post(
        "/learn/train", headers=headers,
        json={"text": text, "filename": filename, "track": track},
    )


# ------------------------------------------------------------------ gating

async def test_student_cannot_upload_or_list(client, store):
    h, _ = await _reg(client, "kb-student@x.com")
    assert (await _upload_text(client, h)).status_code == 403
    assert (await client.get("/learn/documents", headers=h)).status_code == 403
    assert (await client.get("/learn/status", headers=h)).status_code == 403
    assert store.docs == {}


async def test_status_reports_review_requirement(client, instructor, admin):
    t = (await client.get("/learn/status", headers=instructor)).json()
    a = (await client.get("/learn/status", headers=admin)).json()
    assert t["requires_review"] is True
    assert a["requires_review"] is False
    assert ".pdf" in t["supported_formats"]
    assert "custom" in t["allowed_tracks"]


async def test_instructor_cannot_review(client, instructor, store):
    doc_id = (await _upload_text(client, instructor)).json()["document_id"]
    assert (await client.post(f"/learn/documents/{doc_id}/approve", headers=instructor)).status_code == 403
    assert (await client.post(f"/learn/documents/{doc_id}/reject", headers=instructor)).status_code == 403


# --------------------------------------------------------------- lifecycle

async def test_instructor_upload_is_pending_and_not_indexed(client, instructor, store):
    r = await _upload_text(client, instructor, track="DSA")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["review_status"] == "pending"
    assert body["chunks_trained"] == 0
    assert body["track"] == "dsa"
    assert store.docs == {}  # nothing reaches learners before review


async def test_admin_upload_publishes_immediately(client, admin, store):
    r = await _upload_text(client, admin)
    body = r.json()
    assert body["review_status"] == "published"
    assert body["chunks_trained"] == len(store.docs) > 0
    ns = f"upload:{body['document_id']}"
    assert all(d.metadata["problem_id"] == ns for d in store.docs.values())


async def test_approve_indexes_pending_upload(client, instructor, admin, store):
    doc_id = (await _upload_text(client, instructor)).json()["document_id"]
    r = await client.post(f"/learn/documents/{doc_id}/approve", headers=admin)
    assert r.status_code == 200
    assert r.json()["status"] == "published"
    assert r.json()["chunks"] == len(store.docs) > 0

    again = await client.post(f"/learn/documents/{doc_id}/approve", headers=admin)
    assert again.status_code == 409


async def test_reject_pending_records_note(client, instructor, admin, store):
    doc_id = (await _upload_text(client, instructor)).json()["document_id"]
    r = await client.post(
        f"/learn/documents/{doc_id}/reject", headers=admin, json={"note": " off-topic "}
    )
    assert r.status_code == 200
    assert r.json()["status"] == "rejected"
    assert r.json()["review_note"] == "off-topic"
    assert store.docs == {}


async def test_reject_published_unpublishes(client, admin, store):
    doc_id = (await _upload_text(client, admin)).json()["document_id"]
    assert store.docs
    r = await client.post(f"/learn/documents/{doc_id}/reject", headers=admin)
    assert r.status_code == 200
    assert r.json()["chunks"] == 0
    assert store.docs == {}


async def test_reupload_replaces_previous_version(client, admin, store, db):
    first = (await _upload_text(client, admin, text="## A\nold")).json()
    old_ids = set(store.docs)
    second = (await _upload_text(client, admin, text="## A\nnew")).json()

    assert second["document_id"] == first["document_id"]
    assert old_ids.isdisjoint(store.docs)  # old vectors removed
    assert set(store.deleted) == old_ids
    rows = (await db.execute(select(KnowledgeDocument))).scalars().all()
    assert len(rows) == 1


async def test_instructor_reupload_of_published_doc_goes_back_to_review(client, instructor, admin, store):
    doc_id = (await _upload_text(client, instructor, text="## A\nv1")).json()["document_id"]
    await client.post(f"/learn/documents/{doc_id}/approve", headers=admin)
    assert store.docs

    r = (await _upload_text(client, instructor, text="## A\nv2")).json()
    assert r["review_status"] == "pending"
    assert store.docs == {}  # v1 withdrawn; v2 waits for review


async def test_failed_indexing_returns_502_and_keeps_old_version(client, admin, store):
    await _upload_text(client, admin, text="## A\nv1")
    kept = dict(store.docs)
    store.fail_add = True
    r = await _upload_text(client, admin, text="## A\nv2")
    assert r.status_code == 502
    assert store.docs == kept


async def test_vector_delete_failure_does_not_block_db_delete(client, admin, store):
    doc_id = (await _upload_text(client, admin)).json()["document_id"]
    store.fail_delete = True
    r = await client.delete(f"/learn/documents/{doc_id}", headers=admin)
    assert r.status_code == 204
    assert (await client.get(f"/learn/documents/{doc_id}", headers=admin)).status_code == 404


# ------------------------------------------------------- listing & access

async def test_listing_is_scoped_by_role(client, db, instructor, admin, store):
    other = await _make_instructor(client, db, "kb-instructor2@x.com")
    await _upload_text(client, instructor, filename="mine.md")
    await _upload_text(client, other, filename="theirs.md")

    mine = (await client.get("/learn/documents", headers=instructor)).json()
    assert [d["filename"] for d in mine] == ["mine.md"]

    everything = (await client.get("/learn/documents", headers=admin)).json()
    assert {d["filename"] for d in everything} == {"mine.md", "theirs.md"}
    assert {d["owner_email"] for d in everything} == {"kb-instructor@x.com", "kb-instructor2@x.com"}


async def test_listing_filters_by_status(client, instructor, admin, store):
    a = (await _upload_text(client, instructor, filename="a.md")).json()["document_id"]
    await _upload_text(client, instructor, filename="b.md")
    await client.post(f"/learn/documents/{a}/approve", headers=admin)

    pending = (await client.get("/learn/documents?status=pending", headers=admin)).json()
    assert [d["filename"] for d in pending] == ["b.md"]
    assert (await client.get("/learn/documents?status=bogus", headers=admin)).status_code == 400


async def test_detail_includes_preview_for_owner_and_admin(client, db, instructor, admin, store):
    doc_id = (await _upload_text(client, instructor, text="## Tries\nprefix trees")).json()["document_id"]
    for h in (instructor, admin):
        r = await client.get(f"/learn/documents/{doc_id}", headers=h)
        assert r.status_code == 200
        assert "prefix trees" in r.json()["preview"]
        assert r.json()["owner_email"] == "kb-instructor@x.com"

    stranger = await _make_instructor(client, db, "kb-stranger@x.com")
    assert (await client.get(f"/learn/documents/{doc_id}", headers=stranger)).status_code == 404
    assert (await client.delete(f"/learn/documents/{doc_id}", headers=stranger)).status_code == 404


async def test_owner_can_delete_published_doc(client, instructor, admin, store):
    doc_id = (await _upload_text(client, instructor)).json()["document_id"]
    await client.post(f"/learn/documents/{doc_id}/approve", headers=admin)
    assert store.docs
    r = await client.delete(f"/learn/documents/{doc_id}", headers=instructor)
    assert r.status_code == 204
    assert store.docs == {}


async def test_unknown_document_404(client, admin, store):
    assert (await client.post("/learn/documents/nope/approve", headers=admin)).status_code == 404


# --------------------------------------------------------------- validation

async def test_unknown_track_rejected(client, instructor, store):
    r = await _upload_text(client, instructor, track="admin")
    assert r.status_code == 400


async def test_multipart_markdown_upload(client, instructor, store, db):
    r = await client.post(
        "/learn/train", headers=instructor,
        files={"file": ("notes.md", b"# Notes\nTwo pointers...", "text/markdown")},
        data={"track": "algorithm"},
    )
    assert r.status_code == 200, r.text
    doc = (await db.execute(select(KnowledgeDocument))).scalar_one()
    assert doc.text.startswith("# Notes")
    assert doc.track == "algorithm"
    assert doc.file_type == ".md"


async def test_multipart_text_field_without_file(client, instructor, store):
    r = await client.post(
        "/learn/train", headers=instructor,
        data={"text": "pasted", "filename": "pasted.txt"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["filename"] == "pasted.txt"


async def test_unsupported_extension_rejected(client, instructor, store):
    r = await client.post(
        "/learn/train", headers=instructor,
        files={"file": ("run.exe", b"MZ...", "application/octet-stream")},
    )
    assert r.status_code == 400


async def test_empty_extraction_rejected(client, instructor, store):
    r = await client.post(
        "/learn/train", headers=instructor,
        files={"file": ("blank.txt", b"   \n  ", "text/plain")},
    )
    assert r.status_code == 400
    assert "Could not extract" in r.json()["detail"]


async def test_parser_value_error_is_400(client, instructor, store, monkeypatch):
    def bad(*_):
        raise ValueError("PDF support requires the 'pypdf' package")

    monkeypatch.setattr(learn_router, "extract_text_from_file", bad)
    r = await client.post(
        "/learn/train", headers=instructor,
        files={"file": ("a.pdf", b"%PDF", "application/pdf")},
    )
    assert r.status_code == 400
    assert "pypdf" in r.json()["detail"]


async def test_parser_crash_is_400_without_internals(client, instructor, store, monkeypatch):
    def boom(*_):
        raise RuntimeError("secret internal path /srv/x")

    monkeypatch.setattr(learn_router, "extract_text_from_file", boom)
    r = await client.post(
        "/learn/train", headers=instructor,
        files={"file": ("a.docx", b"PK", "application/octet-stream")},
    )
    assert r.status_code == 400
    assert "secret" not in r.json()["detail"]


async def test_oversized_upload_rejected(client, instructor, store, monkeypatch):
    monkeypatch.setattr(learn_router, "MAX_UPLOAD_BYTES", 10)
    r = await client.post(
        "/learn/train", headers=instructor,
        files={"file": ("big.txt", b"x" * 11, "text/plain")},
    )
    assert r.status_code == 413


async def test_overlong_text_rejected(client, instructor, store, monkeypatch):
    monkeypatch.setattr(learn_router, "MAX_TEXT_CHARS", 5)
    r = await _upload_text(client, instructor, text="123456")
    assert r.status_code == 413


async def test_empty_request_rejected(client, instructor, store):
    r = await client.post("/learn/train", headers=instructor, json={"text": "  "})
    assert r.status_code == 400


async def test_non_object_json_rejected(client, instructor, store):
    r = await client.post("/learn/train", headers=instructor, json=["x"])
    assert r.status_code == 400


async def test_malformed_json_rejected(client, instructor, store):
    r = await client.post(
        "/learn/train",
        headers={**instructor, "Content-Type": "application/json"},
        content=b"{not json",
    )
    assert r.status_code == 400


async def test_unsupported_content_type_rejected(client, instructor, store):
    r = await client.post(
        "/learn/train",
        headers={**instructor, "Content-Type": "text/plain"},
        content=b"raw",
    )
    assert r.status_code == 415


def test_chunk_ids_tolerates_corrupt_json():
    doc = KnowledgeDocument(chunk_ids="{broken")
    assert learn_router._chunk_ids(doc) == []
    doc.chunk_ids = json.dumps({"not": "a list"})
    assert learn_router._chunk_ids(doc) == []
