# /learn: teacher/admin document uploads into the RAG knowledge base.
# The vector store is mocked — these check gating, validation, parsing, and
# that uploads can never overwrite curated problem chunks.
import io
import zipfile

import pytest

from app.core.config import settings
from app.routers import learn as learn_router
from app.services import knowledge_base
from app.services.document_parser import extract_text_from_file


async def _reg(client, email):
    r = await client.post("/auth/register", json={"email": email, "password": "password123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def trained(monkeypatch):
    """Captures train_from_document calls instead of embedding anything."""
    calls = []

    def fake_train(filename, text, user_id, track):
        calls.append({"filename": filename, "text": text, "user_id": user_id, "track": track})
        return 3

    monkeypatch.setattr(learn_router, "train_from_document", fake_train)
    return calls


@pytest.fixture
async def teacher(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_emails", "kb-admin@x.com")
    return await _reg(client, "kb-admin@x.com")


async def test_student_cannot_train(client, trained):
    h = await _reg(client, "kb-student@x.com")
    r = await client.post("/learn/train", headers=h, json={"text": "poison"})
    assert r.status_code == 403
    assert trained == []


async def test_json_text_is_trained(client, teacher, trained):
    r = await client.post(
        "/learn/train", headers=teacher,
        json={"text": "## Heaps\nA heap is...", "filename": "heaps.md", "track": "DSA"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["chunks_trained"] == 3
    assert trained[0]["track"] == "dsa"
    assert trained[0]["filename"] == "heaps.md"


async def test_unknown_track_rejected(client, teacher, trained):
    r = await client.post("/learn/train", headers=teacher, json={"text": "x", "track": "admin"})
    assert r.status_code == 400
    assert trained == []


async def test_multipart_markdown_upload(client, teacher, trained):
    r = await client.post(
        "/learn/train", headers=teacher,
        files={"file": ("notes.md", b"# Notes\nTwo pointers...", "text/markdown")},
        data={"track": "algorithm"},
    )
    assert r.status_code == 200, r.text
    assert trained[0]["text"].startswith("# Notes")
    assert trained[0]["track"] == "algorithm"


async def test_unsupported_extension_rejected(client, teacher, trained):
    r = await client.post(
        "/learn/train", headers=teacher,
        files={"file": ("run.exe", b"MZ...", "application/octet-stream")},
    )
    assert r.status_code == 400
    assert trained == []


async def test_oversized_upload_rejected(client, teacher, trained, monkeypatch):
    monkeypatch.setattr(learn_router, "MAX_UPLOAD_BYTES", 10)
    r = await client.post(
        "/learn/train", headers=teacher,
        files={"file": ("big.txt", b"x" * 11, "text/plain")},
    )
    assert r.status_code == 413
    assert trained == []


def test_upload_never_overwrites_curated_chunks(monkeypatch):
    """An upload named two-sum.md must not delete the curated two-sum docs."""

    class FakeStore:
        def __init__(self):
            self.deleted, self.added = [], []

        def delete(self, where):
            self.deleted.append(where)

        def add_documents(self, docs):
            self.added.extend(docs)

    store = FakeStore()
    monkeypatch.setattr(knowledge_base, "get_vectorstore", lambda: store)

    n = knowledge_base.train_from_document("two-sum.md", "## Notes\nmy notes", user_id="u1")
    assert n == len(store.added) > 0
    assert store.deleted == [{"problem_id": "upload:u1:two-sum"}]
    assert all(d.metadata["problem_id"] == "upload:u1:two-sum" for d in store.added)
    assert all(d.metadata["track"] == "custom" for d in store.added)


def test_docx_text_extracted_without_field_codes():
    w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    xml = (
        f'<w:document xmlns:w="{w}"><w:body>'
        "<w:p><w:r><w:t>Binary </w:t></w:r><w:r><w:t>search</w:t></w:r></w:p>"
        "<w:p><w:r><w:instrText>PAGE</w:instrText></w:r></w:p>"
        "<w:p><w:r><w:t>halves the range</w:t></w:r></w:p>"
        "</w:body></w:document>"
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("word/document.xml", xml)
    text = extract_text_from_file("notes.docx", buf.getvalue())
    assert "Binary search" in text
    assert "halves the range" in text
    assert "PAGE" not in text
