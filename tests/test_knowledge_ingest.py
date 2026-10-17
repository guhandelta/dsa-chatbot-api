# Document parsing and knowledge-base indexing, with the vector store and
# embedding providers faked — no network, no API keys.
import io
import sys
import zipfile

import pytest

from app.core.config import settings
from app.services import document_parser as dp
from app.services import knowledge_base as kb


class FakeStore:
    def __init__(self):
        self.added, self.deleted_ids, self.deleted_where = [], [], []
        self.collection_dropped = False

    def add_documents(self, docs, ids=None):
        start = len(self.added)
        self.added.extend(docs)
        return ids if ids is not None else [f"id{start + i}" for i in range(len(docs))]

    def delete(self, ids=None, where=None):
        if ids is not None:
            self.deleted_ids.extend(ids)
        if where is not None:
            self.deleted_where.append(where)

    def delete_collection(self):
        self.collection_dropped = True


@pytest.fixture
def store(monkeypatch):
    s = FakeStore()
    monkeypatch.setattr(kb, "get_vectorstore", lambda: s)
    return s


@pytest.fixture
def no_sleep(monkeypatch):
    sleeps = []
    monkeypatch.setattr(kb.time, "sleep", lambda s: sleeps.append(s))
    return sleeps


# ================================================================ parsing

def _docx_bytes(paragraphs, table_rows=()):
    import docx

    d = docx.Document()
    for p in paragraphs:
        d.add_paragraph(p)
    if table_rows:
        t = d.add_table(rows=len(table_rows), cols=len(table_rows[0]))
        for r, row in enumerate(table_rows):
            for c, val in enumerate(row):
                t.cell(r, c).text = val
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


def test_text_decodes_utf8_and_falls_back_to_latin1():
    assert dp.extract_text_from_file("a.txt", "héllo".encode("utf-8")) == "héllo"
    assert dp.extract_text_from_file("a.md", "café".encode("latin-1")) == "café"


def test_text_decoder_last_resort_replaces(monkeypatch):
    class Undecodable(bytes):
        def decode(self, enc="utf-8", errors="strict"):
            if errors == "strict":
                raise UnicodeDecodeError(enc, b"", 0, 1, "nope")
            return "replaced"

    assert dp.parse_text_or_markdown(Undecodable(b"x")) == "replaced"


def test_unsupported_extension_raises():
    with pytest.raises(ValueError):
        dp.extract_text_from_file("a.exe", b"")


def test_docx_with_python_docx_includes_tables():
    data = _docx_bytes(["Graphs", "BFS explores layer by layer"], [("Algo", "Cost"), ("BFS", "O(V+E)")])
    text = dp.extract_text_from_file("g.docx", data)
    assert "BFS explores layer by layer" in text
    assert "BFS O(V+E)" in text


def test_docx_native_fallback_skips_field_codes(monkeypatch):
    monkeypatch.setitem(sys.modules, "docx", None)  # force the stdlib path
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
    text = dp.extract_text_from_file("notes.docx", buf.getvalue())
    assert text == "Binary search\n\nhalves the range"


def test_docx_garbage_returns_empty():
    assert dp.parse_docx(b"not a zip") == ""


def test_doc_that_is_really_docx():
    data = _docx_bytes(["Legacy extension, modern content"])
    assert "Legacy extension" in dp.extract_text_from_file("old.doc", data)


def test_binary_doc_falls_back_to_printable_runs():
    data = b"\x00\x01Heaps are trees\x00\x02\x03ok\xff"
    text = dp.extract_text_from_file("old.doc", data)
    assert "Heaps are trees" in text
    assert "ok" not in text.split("\n")  # runs under 4 chars are dropped


def test_pdf_extracts_text_with_pypdf(monkeypatch):
    class Page:
        def __init__(self, t):
            self.t = t

        def extract_text(self):
            return self.t

    class Reader:
        def __init__(self, _):
            self.pages = [Page(" Dijkstra "), Page(""), Page(None), Page("relaxes edges")]

    fake = type(sys)("pypdf")
    fake.PdfReader = Reader
    monkeypatch.setitem(sys.modules, "pypdf", fake)
    assert dp.extract_text_from_file("a.pdf", b"%PDF") == "Dijkstra\n\nrelaxes edges"


def test_pdf_without_pypdf_is_a_clear_error(monkeypatch):
    monkeypatch.setitem(sys.modules, "pypdf", None)
    with pytest.raises(ValueError, match="pypdf"):
        dp.extract_text_from_file("a.pdf", b"%PDF")


def test_real_pdf_round_trip():
    """Blank page through the real pypdf: no text, no crash."""
    import pypdf

    w = pypdf.PdfWriter()
    w.add_blank_page(width=72, height=72)
    buf = io.BytesIO()
    w.write(buf)
    assert dp.extract_text_from_file("blank.pdf", buf.getvalue()) == ""


# ============================================================== splitting

def test_markdown_split_by_headings_with_meta_and_language():
    md = (
        "## Sorting\nIntro.\n"
        "### Merge sort\nMeta: difficulty=medium | stable-sort=yes\nSplits in half.\n"
        "#### Merge sort — Python\n```python\ndef ms(a): ...\n```\n"
        "#### Merge sort — All languages\nSame idea everywhere.\n"
    )
    chunks = kb.split_document_for_training("s.md", md, stem="upload:d1", track="custom", user_id="u1")
    assert len(chunks) >= 3
    assert all(c.metadata["problem_id"] == "upload:d1" for c in chunks)
    assert all(c.metadata["user_id"] == "u1" for c in chunks)
    meta_chunk = next(c for c in chunks if "Meta:" in c.page_content)
    assert meta_chunk.metadata["doc_difficulty"] == "medium"
    assert meta_chunk.metadata["doc_stable_sort"] == "yes"
    py = next(c for c in chunks if c.metadata.get("snippet") == "Merge sort — Python")
    assert py.metadata["language"] == "python"
    general = next(c for c in chunks if c.metadata.get("snippet") == "Merge sort — All languages")
    assert "language" not in general.metadata


def test_long_markdown_section_is_sub_split():
    md = "## Big\n" + ("word " * 800)
    chunks = kb.split_document_for_training("b.md", md, stem="s", track="dsa")
    assert len(chunks) > 1
    assert all(len(c.page_content) <= 1200 for c in chunks)
    assert "user_id" not in chunks[0].metadata


def test_plain_text_uses_character_splitter():
    chunks = kb.split_document_for_training("n.txt", "abc " * 600, stem="s", track="dsa")
    assert len(chunks) > 1
    assert all(c.metadata["source"] == "n.txt" for c in chunks)


# =============================================================== indexing

def test_index_uploaded_document_namespaces_and_returns_ids(store):
    ids = kb.index_uploaded_document("doc-1", "two-sum.md", "## Notes\nmine", track="custom", user_id="u1")
    assert len(ids) == 1 and len(ids[0]) == 36
    assert store.added[0].metadata["problem_id"] == "upload:doc-1"
    assert store.added[0].metadata["track"] == "custom"


def test_index_blank_document_writes_nothing(store):
    assert kb.index_uploaded_document("d", "a.md", "   ") == []
    assert store.added == []


def test_remove_chunks_deletes_by_id(store):
    kb.remove_chunks(["a", "b"])
    kb.remove_chunks([])
    assert store.deleted_ids == ["a", "b"]


def test_batches_are_paced(no_sleep):
    s = FakeStore()
    ids = kb.add_documents_in_batches(s, list(range(5)), batch_size=2, delay_between_batches=0.5)
    assert ids == ["id0", "id1", "id2", "id3", "id4"]
    assert no_sleep == [0.5, 0.5]  # between batches, not after the last


def test_empty_batch_is_noop():
    assert kb.add_documents_in_batches(FakeStore(), []) == []


class Flaky(FakeStore):
    def __init__(self, errors):
        super().__init__()
        self.errors = list(errors)

    def add_documents(self, docs):
        if self.errors:
            raise RuntimeError(self.errors.pop(0))
        return super().add_documents(docs)


def test_rate_limit_honours_retry_hint(no_sleep):
    s = Flaky(["429 quota exceeded, retry in 2.5s", "RESOURCE_EXHAUSTED seconds: 4"])
    assert kb.add_documents_in_batches(s, ["a"]) == ["id0"]
    assert no_sleep == [5.5, 7.0]  # hint + 3s safety margin


def test_rate_limit_without_hint_backs_off_exponentially(no_sleep):
    s = Flaky(["rate_limit", "rate_limit"])
    kb.add_documents_in_batches(s, ["a"])
    assert no_sleep == [15.0, 30.0]


def test_rate_limit_gives_up_after_max_retries(no_sleep):
    s = Flaky(["429"] * 3)
    with pytest.raises(RuntimeError):
        kb.add_documents_in_batches(s, ["a"], max_retries=3)
    assert len(no_sleep) == 2


def test_non_rate_limit_error_is_raised_immediately(no_sleep):
    with pytest.raises(RuntimeError, match="bad request"):
        kb.add_documents_in_batches(Flaky(["bad request"]), ["a"])
    assert no_sleep == []


def test_upsert_and_delete_problem(store):
    n = kb.upsert_problem("two-sum", "# Two Sum\n" + "x " * 600, track="dsa", language="python")
    assert n == len(store.added) > 1
    assert store.added[0].metadata["language"] == "python"
    kb.delete_problem("two-sum")
    assert store.deleted_where == [{"problem_id": "two-sum"}] * 2


def test_upsert_and_delete_tolerate_store_errors(monkeypatch):
    class Grumpy(FakeStore):
        def delete(self, **_):
            raise RuntimeError("empty collection")

    s = Grumpy()
    monkeypatch.setattr(kb, "get_vectorstore", lambda: s)
    assert kb.upsert_problem("p", "short", track="dsa") == 1
    kb.delete_problem("p")  # swallowed


def test_ingest_documents_tags_track_and_replaces_collection(store, tmp_path, capsys):
    (tmp_path / "lang").mkdir()
    (tmp_path / "lang" / "py.md").write_text(
        "---\ntrack: language\nlanguage: python\n---\n# Python basics\nLists and dicts.\n"
    )
    (tmp_path / "two-sum.md").write_text("# Two Sum (LC 1) — Easy — Array\nFind two.\n")
    kb.ingest_documents(str(tmp_path))

    assert not store.collection_dropped
    assert {"catalog": "release-v1"} in store.deleted_where
    by_id = {d.metadata["problem_id"]: d for d in store.added}
    assert by_id["py"].metadata["track"] == "language"
    assert by_id["py"].metadata["language"] == "python"
    assert by_id["two-sum"].metadata["track"] == "dsa"
    assert "Ingested" in capsys.readouterr().out


def test_ingest_falls_back_when_metadata_unparseable(store, tmp_path, monkeypatch):
    (tmp_path / "x.md").write_text("# X\nbody\n")
    import app.services.content_catalog as cc

    monkeypatch.setattr(cc, "parse_file", lambda p: (_ for _ in ()).throw(ValueError("bad")))
    kb.ingest_documents(str(tmp_path))
    assert store.added[0].metadata["track"] == "dsa"


def test_ingest_tolerates_missing_collection(tmp_path, monkeypatch):
    class Fresh(FakeStore):
        def delete_collection(self):
            raise RuntimeError("no collection yet")

    s = Fresh()
    monkeypatch.setattr(kb, "get_vectorstore", lambda: s)
    (tmp_path / "a.md").write_text("# A\nbody\n")
    kb.ingest_documents(str(tmp_path))
    assert s.added


def test_ingest_empty_directory(store, tmp_path, capsys):
    kb.ingest_documents(str(tmp_path / "missing"))
    assert "nothing to ingest" in capsys.readouterr().out
    assert store.added == []


# ============================================================= providers

def test_explicit_deterministic_embeddings(monkeypatch):
    from langchain_core.embeddings import DeterministicFakeEmbedding

    monkeypatch.setattr(settings, "embedding_provider", "deterministic")
    assert isinstance(kb.get_embeddings(), DeterministicFakeEmbedding)


def test_no_keys_requires_real_provider(monkeypatch):
    from langchain_core.embeddings import DeterministicFakeEmbedding

    monkeypatch.setattr(settings, "embedding_provider", "")
    monkeypatch.setattr(settings, "google_api_key", "")
    monkeypatch.setattr(settings, "openai_api_key", "")
    with pytest.raises(RuntimeError, match="embedding provider"):
        kb.get_embeddings()


def test_openai_embeddings_when_selected(monkeypatch):
    from langchain_openai import OpenAIEmbeddings

    monkeypatch.setattr(settings, "embedding_provider", "openai")
    monkeypatch.setattr(settings, "openai_api_key", "sk-test")
    assert isinstance(kb.get_embeddings(), OpenAIEmbeddings)


def test_auto_prefers_google_when_key_present(monkeypatch):
    import langchain_google_genai

    class FakeGoogle:
        def __init__(self, **kw):
            self.kw = kw

    monkeypatch.setattr(langchain_google_genai, "GoogleGenerativeAIEmbeddings", FakeGoogle)
    monkeypatch.setattr(settings, "embedding_provider", "")
    monkeypatch.setattr(settings, "google_api_key", "g-test")
    emb = kb.get_embeddings()
    assert isinstance(emb, FakeGoogle)
    assert emb.kw["google_api_key"] == "g-test"


def test_google_failure_falls_back_to_openai(monkeypatch):
    import langchain_google_genai
    from langchain_openai import OpenAIEmbeddings

    def broken(**_):
        raise RuntimeError("bad key format")

    monkeypatch.setattr(langchain_google_genai, "GoogleGenerativeAIEmbeddings", broken)
    monkeypatch.setattr(settings, "embedding_provider", "google")
    monkeypatch.setattr(settings, "google_api_key", "g-test")
    monkeypatch.setattr(settings, "openai_api_key", "sk-test")
    assert isinstance(kb.get_embeddings(), OpenAIEmbeddings)


def test_openai_failure_does_not_silently_use_fake_embeddings(monkeypatch):
    import langchain_openai
    from langchain_core.embeddings import DeterministicFakeEmbedding

    def broken(**_):
        raise RuntimeError("bad")

    monkeypatch.setattr(langchain_openai, "OpenAIEmbeddings", broken)
    monkeypatch.setattr(settings, "embedding_provider", "openai")
    monkeypatch.setattr(settings, "openai_api_key", "sk-test")
    with pytest.raises(RuntimeError, match="embedding provider"):
        kb.get_embeddings()


def test_vectorstore_backends(monkeypatch):
    import langchain_chroma
    import langchain_postgres

    captured = {}

    class FakeChroma:
        def __init__(self, **kw):
            captured["chroma"] = kw

    class FakePG:
        def __init__(self, **kw):
            captured["pg"] = kw

    monkeypatch.setattr(langchain_chroma, "Chroma", FakeChroma)
    monkeypatch.setattr(langchain_postgres, "PGVector", FakePG)
    monkeypatch.setattr(kb, "get_embeddings", lambda: "emb")

    monkeypatch.setattr(settings, "vector_store", "chroma")
    assert isinstance(kb.get_vectorstore(), FakeChroma)
    assert captured["chroma"]["collection_name"] == kb.COLLECTION_NAME

    monkeypatch.setattr(settings, "vector_store", "pgvector")
    monkeypatch.setattr(settings, "vector_database_url", "postgresql+asyncpg://u@h/db")
    assert isinstance(kb.get_vectorstore(), FakePG)
    assert captured["pg"]["connection"] == "postgresql+psycopg://u@h/db"


@pytest.mark.parametrize("url,expected", [
    ("postgres://u@h/db", "postgresql+psycopg://u@h/db"),
    ("postgresql+asyncpg://u@h/db", "postgresql+psycopg://u@h/db"),
    ("sqlite+aiosqlite:///x.db", "sqlite:///x.db"),
])
def test_pgvector_connection_string(monkeypatch, url, expected):
    monkeypatch.setattr(settings, "vector_database_url", url)
    assert kb.pgvector_connection_string() == expected


def test_uploaded_reference_is_answer_safe_and_retrievable():
    chunks = kb.split_document_for_training('lesson.md', '## Notes\nUseful explanation.\n## Solutions\nSECRET', stem='upload:x', track='custom')
    assert chunks and all(c.metadata['contains_answer'] is False for c in chunks)
    assert all('SECRET' not in c.page_content for c in chunks)
