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
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings

COLLECTION_NAME = "dsa_problems"


def get_embeddings() -> OpenAIEmbeddings:
    """Embedding model. Shared by both backends so vectors stay comparable —
    switching backends does NOT require changing this, but changing the
    embedding model DOES require re-ingesting everything."""
    return OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model=settings.embedding_model,
    )


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
            use_jsonb=True,   # metadata filters (track, problem_id) need JSONB
        )

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
    get_vectorstore().add_documents(chunks)
    print(f"Ingested {len(chunks)} chunks from {len(documents)} problems into ChromaDB.")


if __name__ == "__main__":
    ingest_documents()


def upsert_problem(problem_id: str, markdown: str, track: str = "dsa",
                   language: str | None = None) -> int:
    """Add or replace ONE problem in the vector store without rebuilding it.

    Deletes any existing chunks for this problem_id first, so re-training an
    existing problem replaces it instead of duplicating chunks (the bug that
    made re-running the ingest CLI grow the collection every time).
    Returns the number of chunks written.
    """
    from langchain_core.documents import Document

    vs = get_vectorstore()
    # Remove prior chunks for this problem (no-op if it is new)
    try:
        vs.delete(where={"problem_id": problem_id})
    except Exception:  # collection may be empty on first run
        pass

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(
        [Document(page_content=markdown, metadata={
            "problem_id": problem_id,
            "source": f"{problem_id}.md",
            "track": track,
            **({"language": language} if language else {}),
        })]
    )
    vs.add_documents(chunks)
    return len(chunks)


def delete_problem(problem_id: str) -> None:
    """Remove a problem's chunks from the vector store."""
    vs = get_vectorstore()
    try:
        vs.delete(where={"problem_id": problem_id})
    except Exception:
        pass
