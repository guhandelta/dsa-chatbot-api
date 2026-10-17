# /learn endpoints — instructors and admins feed extra reference documents
# (.txt, .md, .pdf, .docx, .doc) or pasted notes into the RAG knowledge base.
#
# Uploaded material is retrieved for EVERY learner's chat, which makes it a
# prompt-injection surface. So writing is limited to instructors/admins, and an
# instructor's upload waits for admin review before it is indexed:
#
#   instructor uploads ──▶ pending ──approve──▶ published (indexed)
#                              └─reject───▶ rejected  (never indexed)
#   admin uploads   ──────────────────────▶ published
import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
# request.form() yields Starlette's UploadFile; FastAPI's is a subclass, so an
# isinstance check against fastapi.UploadFile never matches a real upload.
from starlette.datastructures import UploadFile

from app.core.config import settings
from app.core.security import require_admin, require_instructor
from app.db.database import get_session
from app.db.models import KnowledgeDocument, User
from app.models.schemas import (
    KnowledgeDocumentDetail,
    KnowledgeDocumentOut,
    KnowledgeReviewRequest,
    LearnTrainResponse,
)
from app.services.document_parser import ALLOWED_EXTENSIONS, extract_text_from_file
from app.services.knowledge_base import index_uploaded_document, UploadIndexError
from app.services.maintenance import queue_cleanup, drain_cleanup

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/learn", tags=["learn"])

# "custom" is retrieved alongside whichever track the learner is chatting in.
ALLOWED_TRACKS = {"dsa", "algorithm", "language", "custom"}
KNOWLEDGE_STATUSES = {"pending", "published", "rejected"}

# Every chunk costs an embedding call; bound what one request can spend.
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_TEXT_CHARS = 500_000
PREVIEW_CHARS = 4000


def _clean_track(track: object) -> str:
    value = str(track or "custom").strip().lower()
    if value not in ALLOWED_TRACKS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown track '{value}'. Allowed: {', '.join(sorted(ALLOWED_TRACKS))}",
        )
    return value


def _chunk_ids(doc: KnowledgeDocument) -> list[str]:
    try:
        ids = json.loads(doc.chunk_ids or "[]")
    except ValueError:
        return []
    return [str(i) for i in ids] if isinstance(ids, list) else []


def _out(doc: KnowledgeDocument, owner_email: str = "") -> KnowledgeDocumentOut:
    from app.services.uploaded_knowledge import project, infer_language, PROJECTION_VERSION
    projected = project(doc.id, doc.filename, doc.text, doc.track, doc.language)
    language = doc.language or infer_language(doc.filename)
    retrieval_status = ("awaiting_approval" if doc.status != "published" else
                        "language_review_required" if not language else
                        "no_reference_text" if not projected else "available")
    return KnowledgeDocumentOut(
        id=doc.id,
        owner_id=doc.owner_id,
        owner_email=owner_email,
        filename=doc.filename,
        file_type=doc.file_type,
        track=doc.track,
        status=doc.status,
        characters=doc.characters,
        chunks=len(_chunk_ids(doc)),
        review_note=doc.review_note,
        created_at=doc.created_at,
        reviewed_at=doc.reviewed_at,
        retrieval_status=retrieval_status,
        reference_language=language,
        reference_chunks=len(projected),
        projection_version=PROJECTION_VERSION,
    )


async def _index(doc: KnowledgeDocument, session: AsyncSession) -> list[str]:
    filename = doc.filename
    try:
        return await asyncio.to_thread(
            index_uploaded_document, doc.id, doc.filename, doc.text, doc.track, doc.owner_id, doc.language
        )
    except Exception as exc:
        # Roll back an attempted replacement before committing its cleanup
        # obligation. Original content and review evidence remain unchanged.
        await session.rollback()
        if isinstance(exc, UploadIndexError):
            queue_cleanup(session, exc.chunk_ids)
            await session.commit()
        logger.exception("Knowledge base indexing failed for '%s'", filename)
        raise HTTPException(
            status_code=502,
            detail="Failed to index the document into the knowledge base. Check the embedding provider and try again.",
        )



def _mark_reviewed(doc: KnowledgeDocument, reviewer: User, new_status: str, note: str = "") -> None:
    doc.status = new_status
    doc.reviewed_by = reviewer.id
    doc.reviewed_at = datetime.now(timezone.utc)
    doc.review_note = note


async def _get_visible(session: AsyncSession, doc_id: str, user: User) -> KnowledgeDocument:
    """Owners see their own documents; admins see everything. Anything else
    is a 404 so ids of other instructors' uploads are not confirmed."""
    doc = await session.get(KnowledgeDocument, doc_id)
    if doc is None or (user.role != "admin" and doc.owner_id != user.id):
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


async def _read_upload(request: Request) -> tuple[str, str, str, str]:
    """Returns (filename, extracted_text, track) from multipart or JSON."""
    content_type = request.headers.get("content-type", "").lower()
    filename = ""
    file_bytes = b""
    text_content = ""
    language = ""

    if "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        uploaded_file = form.get("file")
        track = _clean_track(form.get("track"))
        language = str(form.get("language") or "").strip().lower()
        text_content = str(form.get("text") or "").strip()
        if isinstance(uploaded_file, UploadFile):
            filename = uploaded_file.filename or "document.txt"
            file_bytes = await uploaded_file.read(MAX_UPLOAD_BYTES + 1)
            if len(file_bytes) > MAX_UPLOAD_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=f"File exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit.",
                )
        elif form.get("filename"):
            filename = str(form.get("filename"))
    elif "application/json" in content_type:
        try:
            body = await request.json()
        except ValueError:
            raise HTTPException(status_code=400, detail="Malformed JSON body.")
        if not isinstance(body, dict):
            raise HTTPException(status_code=400, detail="Expected a JSON object.")
        filename = str(body.get("filename") or "pasted_notes.md")
        text_content = str(body.get("text") or body.get("content") or "").strip()
        track = _clean_track(body.get("track"))
        language = str(body.get("language") or "").strip().lower()
    else:
        raise HTTPException(
            status_code=415,
            detail="Send multipart/form-data with a 'file' field, or JSON with a 'text' field.",
        )

    if file_bytes:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )
        try:
            final_text = await asyncio.to_thread(extract_text_from_file, filename, file_bytes)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception:
            logger.exception("Failed to parse document '%s'", filename)
            raise HTTPException(status_code=400, detail=f"Failed to parse '{filename}'.")
        if not final_text.strip():
            raise HTTPException(
                status_code=400,
                detail=f"Could not extract readable text from '{filename}'. Please ensure the document is not empty, scanned, or corrupted.",
            )
    elif text_content:
        final_text = text_content
        filename = filename or "custom_notes.md"
    else:
        raise HTTPException(
            status_code=400,
            detail="No document file or text content provided to train the knowledge base.",
        )

    if len(final_text) > MAX_TEXT_CHARS:
        raise HTTPException(
            status_code=413,
            detail=f"Document is too long ({len(final_text):,} characters; limit {MAX_TEXT_CHARS:,}). Split it and upload the parts.",
        )
    if language and language not in {"javascript", "java", "typescript", "python", "cpp", "c", "rust", "go", "ruby"}:
        raise HTTPException(422, "Unsupported reference language.")
    from app.services.uploaded_knowledge import infer_language
    inferred = infer_language(filename)
    if language and inferred and language != inferred:
        raise HTTPException(422, "The selected language conflicts with the filename. Choose the source language.")
    return filename, final_text, track, language


@router.get("/status")
async def learn_status(current_user: User = Depends(require_instructor)):
    """Returns the status of the knowledge base training pipeline and supported formats."""
    return {
        "status": "online",
        "supported_formats": sorted(ALLOWED_EXTENSIONS),
        "allowed_tracks": sorted(ALLOWED_TRACKS),
        "max_upload_mb": MAX_UPLOAD_BYTES // (1024 * 1024),
        "vector_store": settings.vector_store,
        "embedding_provider": settings.embedding_provider or "auto",
        "requires_review": current_user.role != "admin",
    }


@router.post("/train", response_model=LearnTrainResponse, status_code=status.HTTP_200_OK)
async def train_knowledge_base(
    request: Request,
    current_user: User = Depends(require_instructor),
    session: AsyncSession = Depends(get_session),
):
    """Uploads a document or pasted text for the knowledge base.

    Accepts either multipart/form-data (`file`, optional `track`, optional
    `text`) or JSON (`{"text": ..., "filename": ..., "track": ...}`).
    Re-uploading a filename you already uploaded replaces that document.
    """
    filename, final_text, track, language = await _read_upload(request)

    existing = (
        await session.execute(
            select(KnowledgeDocument).where(
                KnowledgeDocument.owner_id == current_user.id,
                KnowledgeDocument.filename == filename,
            )
        )
    ).scalar_one_or_none()
    old_ids = _chunk_ids(existing) if existing else []
    doc = existing or KnowledgeDocument(owner_id=current_user.id, filename=filename)
    if existing is None:
        session.add(doc)
        await session.flush()  # assigns doc.id, used as the vector namespace

    doc.file_type = Path(filename).suffix.lower() or ".txt"
    doc.track = track
    doc.language = language
    doc.text = final_text
    doc.characters = len(final_text)
    doc.chunk_ids = "[]"
    doc.review_note = ""
    doc.reviewed_by = ""
    doc.reviewed_at = None

    if current_user.role == "admin":
        # Index before touching the old version, so a failed re-upload
        # leaves the previous published copy in place.
        new_ids = await _index(doc, session)
        doc.chunk_ids = json.dumps(new_ids)
        _mark_reviewed(doc, current_user, "published")
        message = f"Published '{filename}' to the knowledge base ({len(new_ids)} chunk(s), track: {track})."
    else:
        new_ids = []
        doc.status = "pending"
        message = f"Uploaded '{filename}'. It will be used in chat once an admin approves it."

    queue_cleanup(session, old_ids)
    await session.commit()
    await drain_cleanup(session)

    view = _out(doc)
    return LearnTrainResponse(
        status="success",
        document_id=doc.id,
        review_status=doc.status,
        filename=filename,
        file_type=doc.file_type,
        characters_extracted=len(final_text),
        chunks_trained=len(new_ids),
        track=track,
        message=message,
        retrieval_status=view.retrieval_status,
        reference_language=view.reference_language,
        reference_chunks=view.reference_chunks,
    )


@router.get("/documents", response_model=list[KnowledgeDocumentOut])
async def list_documents(
    status_filter: str | None = Query(default=None, alias="status"),
    current_user: User = Depends(require_instructor),
    session: AsyncSession = Depends(get_session),
):
    """Instructors see their own uploads; admins see everyone's (the review
    queue is `?status=pending`)."""
    if status_filter is not None and status_filter not in KNOWLEDGE_STATUSES:
        raise HTTPException(status_code=400, detail=f"Unknown status '{status_filter}'.")
    stmt = (
        select(KnowledgeDocument, User.email)
        .join(User, User.id == KnowledgeDocument.owner_id)
        .order_by(KnowledgeDocument.created_at.desc())
    )
    if current_user.role != "admin":
        stmt = stmt.where(KnowledgeDocument.owner_id == current_user.id)
    if status_filter:
        stmt = stmt.where(KnowledgeDocument.status == status_filter)
    rows = (await session.execute(stmt)).all()
    return [_out(doc, email) for doc, email in rows]


@router.get("/documents/{doc_id}", response_model=KnowledgeDocumentDetail)
async def get_document(
    doc_id: str,
    current_user: User = Depends(require_instructor),
    session: AsyncSession = Depends(get_session),
):
    doc = await _get_visible(session, doc_id, current_user)
    owner = await session.get(User, doc.owner_id)
    return KnowledgeDocumentDetail(
        **_out(doc, owner.email if owner else "").model_dump(),
        preview=doc.text[:PREVIEW_CHARS],
    )


@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: str,
    current_user: User = Depends(require_instructor),
    session: AsyncSession = Depends(get_session),
):
    doc = await _get_visible(session, doc_id, current_user)
    ids = _chunk_ids(doc)
    queue_cleanup(session, ids)
    await session.delete(doc)
    await session.commit()
    await drain_cleanup(session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/documents/{doc_id}/approve", response_model=KnowledgeDocumentOut)
async def approve_document(
    doc_id: str,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    doc = await _get_visible(session, doc_id, admin)
    if doc.status == "published":
        raise HTTPException(status_code=409, detail="Document is already published.")
    ids = await _index(doc, session)
    doc.chunk_ids = json.dumps(ids)
    _mark_reviewed(doc, admin, "published")
    await session.commit()
    return _out(doc)


@router.post("/documents/{doc_id}/reject", response_model=KnowledgeDocumentOut)
async def reject_document(
    doc_id: str,
    body: KnowledgeReviewRequest | None = None,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Rejects a pending upload, or unpublishes a published one."""
    doc = await _get_visible(session, doc_id, admin)
    ids = _chunk_ids(doc)
    doc.chunk_ids = "[]"
    _mark_reviewed(doc, admin, "rejected", (body.note if body else "").strip())
    queue_cleanup(session, ids)
    await session.commit()
    await drain_cleanup(session)
    return _out(doc)
