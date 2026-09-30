# Builds and manages the ChromaDB vector store from DSA problem documents.
#
# Each markdown file under data/dsa_problems/ describes ONE problem
# (title, description, examples, constraints, hints, optimal solution).
# The file stem becomes the chunk's `problem_id` metadata, which lets the
# analyzer retrieve a problem's reference docs with an EXACT filter instead
# of hoping semantic similarity on the ID string finds the right chunks.
#
# Seed/refresh the knowledge base with:
#   python -m app.services.knowledge_base
import logging
from pathlib import Path
import re
import time
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "dsa_problems"


def get_embeddings() -> Any:
    """Embedding model. Shared by both backends so vectors stay comparable —
    switching backends does NOT require changing this, but changing the
    embedding model DOES require re-ingesting everything.
    Uses Google Gemini embeddings if available, falls back to OpenAI or Deterministic."""
    provider = (settings.embedding_provider or "").lower().strip()
    if not provider:
        provider = "google" if settings.google_api_key else ("openai" if settings.openai_api_key else "deterministic")

    if provider == "google" and settings.google_api_key:
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            return GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=settings.google_api_key,
            )
        except Exception as exc:
            logger.warning(f"Google embeddings unavailable: {exc}")

    # Reached when OpenAI was chosen, or Google was chosen but unavailable.
    if provider != "deterministic" and settings.openai_api_key:
        try:
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(
                api_key=settings.openai_api_key,
                model=settings.embedding_model,
                request_timeout=15,
                max_retries=2,
            )
        except Exception as exc:
            logger.warning(f"OpenAI embeddings unavailable: {exc}")

    # Last resort so local dev boots without keys. Retrieval is meaningless
    # with these vectors — say so loudly rather than degrade silently.
    logger.warning("No embedding provider available; using fake embeddings (RAG retrieval disabled in effect)")
    from langchain_core.embeddings import DeterministicFakeEmbedding
    return DeterministicFakeEmbedding(size=768)


def get_vectorstore():
    """Returns the configured vector store.

    Two backends, selected by VECTOR_STORE in .env:

      chroma    — embedded, file-backed. Zero setup, good for local work, but
                  it cannot be shared between processes, so horizontal scaling
                  needs a shared volume.
      pgvector  — Postgres with the pgvector extension (Supabase, RDS, Neon,
                  or plain Postgres). One database for users, peppercorns,
                  chat history, learning events, traces AND vectors.

    Both expose the same LangChain VectorStore interface, so every caller in
    this codebase (`similarity_search`, `add_documents`, `delete`) works
    unchanged against either. That is the point: the backend is a
    configuration decision, not a rewrite.
    """
    embeddings = get_embeddings()

    if settings.vector_store == "pgvector":
        # Imported lazily so a Chroma-only install does not need the driver.
        from langchain_postgres import PGVector

        return PGVector(
            embeddings=embeddings,
            collection_name=COLLECTION_NAME,
            connection=pgvector_connection_string(),
            use_jsonb=True,  # metadata filters (track, problem_id) need JSONB
        )

    from langchain_chroma import Chroma

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=settings.chroma_persist_dir,
    )


def pgvector_connection_string() -> str:
    """Connection string for the vector store.

    Defaults to reusing DATABASE_URL, so Supabase users configure ONE
    database URL and get both relational storage and vectors. Override with
    VECTOR_DATABASE_URL only if vectors live somewhere separate.

    langchain-postgres expects a psycopg3 driver, so async drivers used by
    the app's ORM are translated here rather than requiring a second,
    easily-desynchronised env var.
    """
    url = settings.vector_database_url or settings.database_url
    return (
        url.replace("+aiosqlite", "")
        .replace("postgresql+asyncpg://", "postgresql+psycopg://")
        .replace("postgres://", "postgresql+psycopg://")
    )


def ingest_documents(docs_path: str | None = None) -> None:
    """Loads every .md across all content directories, tags each with its
    problem_id + track (+ language for the language track), chunks, and embeds."""
    from langchain_community.document_loaders import DirectoryLoader, TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    from app.services.content_catalog import CONTENT_DIR, LEGACY_DIR, parse_file

    roots = [docs_path] if docs_path else [str(CONTENT_DIR), str(LEGACY_DIR)]
    documents = []
    for root in roots:
        if not Path(root).is_dir():
            continue
        loader = DirectoryLoader(root, glob="**/*.md", loader_cls=TextLoader)
        documents.extend(loader.load())
    if not documents:
        print(f"No .md files found under {docs_path} — nothing to ingest.")
        return

    # Tag every document with problem_id = file name without extension,
    # e.g. data/dsa_problems/two-sum.md -> "two-sum"
    for doc in documents:
        source = doc.metadata.get("source", "")
        stem = Path(source).stem
        doc.metadata["problem_id"] = stem
        try:
            meta = parse_file(Path(source))
            doc.metadata["track"] = meta.track
            if meta.language:
                doc.metadata["language"] = meta.language
        except Exception:
            doc.metadata["track"] = "dsa"

    # Split into overlapping chunks so context isn't lost at boundaries.
    # Metadata (incl. problem_id) is preserved on every chunk.
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    # Drop the existing collection so re-running ingest replaces rather than
    # duplicating every chunk. Both backends expose delete_collection, but it
    # is guarded because a first run has nothing to drop.
    try:
        get_vectorstore().delete_collection()
    except Exception:
        pass

    # add_documents works identically on both backends, unlike the
    # Chroma-specific from_documents() constructor.
    add_documents_in_batches(get_vectorstore(), chunks)
    print(
        f"Ingested {len(chunks)} chunks from {len(documents)} problems into ChromaDB."
    )


def add_documents_in_batches(
    vectorstore: Any,
    chunks: list[Any],
    batch_size: int = 40,
    delay_between_batches: float = 1.0,
    max_retries: int = 6,
) -> int:
    """Adds documents to the vector store in rate-limited batches with
    automatic 429 retry / backoff for providers with strict per-minute quotas
    (such as Google Gemini Free Tier's 100 requests/minute limit)."""
    if not chunks:
        return 0

    total_chunks = len(chunks)
    total_batches = (total_chunks + batch_size - 1) // batch_size
    logger.info(
        f"Adding {total_chunks} chunks to vector store in {total_batches} batches of up to {batch_size}..."
    )

    for i in range(0, total_chunks, batch_size):
        batch = chunks[i : i + batch_size]
        batch_idx = (i // batch_size) + 1

        for attempt in range(1, max_retries + 1):
            try:
                vectorstore.add_documents(batch)
                logger.info(
                    f"Successfully indexed batch {batch_idx}/{total_batches} ({len(batch)} chunks)"
                )
                if i + batch_size < total_chunks and delay_between_batches > 0:
                    time.sleep(delay_between_batches)
                break
            except Exception as exc:
                err_msg = str(exc)
                is_rate_limit = (
                    "429" in err_msg
                    or "quota" in err_msg.lower()
                    or "rate_limit" in err_msg.lower()
                    or "resource_exhausted" in err_msg.lower()
                )

                if is_rate_limit and attempt < max_retries:
                    # Extract suggested retry delay from error if present (e.g. "retry in 48.9s" or "seconds: 48")
                    retry_seconds = None
                    m_sec = re.search(r"retry in (\d+(?:\.\d+)?)s", err_msg, re.IGNORECASE)
                    if m_sec:
                        retry_seconds = float(m_sec.group(1))
                    else:
                        m_delay = re.search(r"seconds:\s*(\d+)", err_msg)
                        if m_delay:
                            retry_seconds = float(m_delay.group(1))

                    wait_time = (retry_seconds + 3.0) if retry_seconds else min(65.0, 15.0 * (2 ** (attempt - 1)))
                    logger.warning(
                        f"Rate limit / quota 429 encountered on batch {batch_idx}/{total_batches} "
                        f"(attempt {attempt}/{max_retries}). Sleeping {wait_time:.1f}s before retry..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.exception(
                        f"Failed to index batch {batch_idx}/{total_batches} after {attempt} attempts: {exc}"
                    )
                    raise exc

    return total_chunks


def split_document_for_training(
    filename: str,
    text_content: str,
    stem: str,
    track: str,
    user_id: str | None = None,
) -> list[Any]:
    """Splits a document intelligently. If the document is Markdown, it splits
    hierarchically along headings (##, ###, ####) and extracts metadata tags;
    otherwise it uses a recursive character splitter."""
    from langchain_core.documents import Document
    from langchain_text_splitters import (
        MarkdownHeaderTextSplitter,
        RecursiveCharacterTextSplitter,
    )

    is_markdown = filename.lower().endswith((".md", ".markdown"))
    chunks: list[Document] = []

    if is_markdown and ("##" in text_content or "###" in text_content):
        headers = [
            ("##", "section"),
            ("###", "subsection"),
            ("####", "snippet"),
        ]
        md_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers, strip_headers=False
        )
        header_docs = md_splitter.split_text(text_content)

        # Sub-split any section that exceeds 1600 characters so chunks stay bite-sized
        sub_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200, chunk_overlap=120
        )
        for hdoc in header_docs:
            if len(hdoc.page_content) > 1600:
                sub_chunks = sub_splitter.split_documents([hdoc])
                chunks.extend(sub_chunks)
            else:
                chunks.append(hdoc)
    else:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=150
        )
        chunks = splitter.split_documents([Document(page_content=text_content)])

    final_chunks: list[Document] = []
    for doc in chunks:
        meta = {
            "problem_id": stem,
            "source": filename,
            "track": track,
            **doc.metadata,
        }
        if user_id:
            meta["user_id"] = user_id

        # Extract Meta: key=value | key=value tags if present in markdown reference documents
        meta_match = re.search(r"Meta:\s*([^\n]+)", doc.page_content)
        if meta_match:
            for item in meta_match.group(1).split("|"):
                if "=" in item:
                    k, v = item.split("=", 1)
                    meta[f"doc_{k.strip().replace('-', '_')}"] = v.strip()

        # Extract code snippet language if heading has `<Topic> — <Language>`
        snippet_hdr = meta.get("snippet", "")
        if "—" in snippet_hdr:
            lang = snippet_hdr.split("—")[-1].strip().lower()
            if lang and lang != "all languages":
                meta["language"] = lang

        final_chunks.append(Document(page_content=doc.page_content, metadata=meta))

    return final_chunks


def upsert_problem(
    problem_id: str, markdown: str, track: str = "dsa", language: str | None = None
) -> int:
    """Add or replace ONE problem in the vector store without rebuilding it.

    Deletes any existing chunks for this problem_id first, so re-training an
    existing problem replaces it instead of duplicating chunks (the bug that
    made re-running the ingest CLI grow the collection every time).
    Returns the number of chunks written.
    """
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    vs = get_vectorstore()
    # Remove prior chunks for this problem (no-op if it is new)
    try:
        vs.delete(where={"problem_id": problem_id})
    except Exception:  # collection may be empty on first run
        pass

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(
        [
            Document(
                page_content=markdown,
                metadata={
                    "problem_id": problem_id,
                    "source": f"{problem_id}.md",
                    "track": track,
                    **({"language": language} if language else {}),
                },
            )
        ]
    )
    add_documents_in_batches(vs, chunks)
    return len(chunks)


def delete_problem(problem_id: str) -> None:
    """Remove a problem's chunks from the vector store."""
    vs = get_vectorstore()
    try:
        vs.delete(where={"problem_id": problem_id})
    except Exception:
        pass


def train_from_document(
    filename: str,
    text_content: str,
    user_id: str | None = None,
    track: str = "custom",
) -> int:
    """Takes extracted text from an uploaded document (.txt, .md, .pdf, .docx, .doc),
    splits it into semantic chunks, and indexes it into the vector store so the
    RAG pipeline can retrieve and use it during chat and mentor sessions.
    Returns the number of chunks added.
    """
    if not text_content or not text_content.strip():
        return 0

    # Namespaced so an upload named "two-sum.md" replaces only the uploader's
    # previous version of that file, never the curated two-sum chunks.
    doc_id = f"upload:{user_id or 'anon'}:{Path(filename).stem}"
    vs = get_vectorstore()

    try:
        vs.delete(where={"problem_id": doc_id})
    except Exception:
        pass

    chunks = split_document_for_training(
        filename=filename,
        text_content=text_content,
        stem=doc_id,
        track=track,
        user_id=user_id,
    )
    add_documents_in_batches(vs, chunks)
    return len(chunks)


if __name__ == "__main__":
    ingest_documents()
