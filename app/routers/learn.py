# /learn endpoints — teachers and admins feed extra reference documents
# (.txt, .md, .pdf, .docx, .doc) or pasted notes into the RAG knowledge base.
#
# Uploaded material is retrieved for EVERY learner's chat, so writing to it
# is restricted to the same roles that can publish training content.
import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status
# request.form() yields Starlette's UploadFile; FastAPI's is a subclass, so an
# isinstance check against fastapi.UploadFile never matches a real upload.
from starlette.datastructures import UploadFile

from app.core.config import settings
from app.core.security import require_teacher
from app.db.models import User
from app.models.schemas import LearnTrainResponse
from app.services.document_parser import ALLOWED_EXTENSIONS, extract_text_from_file
from app.services.knowledge_base import train_from_document

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/learn", tags=["learn"])

# "custom" is retrieved alongside whichever track the learner is chatting in.
ALLOWED_TRACKS = {"dsa", "algorithm", "language", "custom"}

# Every chunk costs an embedding call; bound what one request can spend.
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_TEXT_CHARS = 500_000


def _clean_track(track: str | None) -> str:
    value = (track or "custom").strip().lower()
    if value not in ALLOWED_TRACKS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown track '{value}'. Allowed: {', '.join(sorted(ALLOWED_TRACKS))}",
        )
    return value


@router.get("/status")
async def learn_status(current_user: User = Depends(require_teacher)):
    """Returns the status of the knowledge base training pipeline and supported formats."""
    return {
        "status": "online",
        "supported_formats": sorted(ALLOWED_EXTENSIONS),
        "allowed_tracks": sorted(ALLOWED_TRACKS),
        "max_upload_mb": MAX_UPLOAD_BYTES // (1024 * 1024),
        "vector_store": settings.vector_store,
        "embedding_provider": settings.embedding_provider or "auto",
    }


@router.post("/train", response_model=LearnTrainResponse, status_code=status.HTTP_200_OK)
async def train_knowledge_base(
    request: Request,
    current_user: User = Depends(require_teacher),
):
    """Trains the knowledge base from an uploaded document or pasted text.

    Accepts either multipart/form-data (`file`, optional `track`, optional
    `text`) or JSON (`{"text": ..., "filename": ..., "track": ...}`).
    """
    content_type = request.headers.get("content-type", "").lower()
    filename = ""
    file_bytes = b""
    text_content = ""

    if "multipart/form-data" in content_type:
        form = await request.form()
        uploaded_file = form.get("file")
        track = _clean_track(str(form.get("track") or "custom"))
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
        body = await request.json()
        if not isinstance(body, dict):
            raise HTTPException(status_code=400, detail="Expected a JSON object.")
        filename = str(body.get("filename") or "pasted_notes.md")
        text_content = str(body.get("text") or body.get("content") or "").strip()
        track = _clean_track(body.get("track"))
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
        doc_name = filename
    elif text_content:
        final_text = text_content
        doc_name = filename or "custom_notes.md"
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

    try:
        chunks_count = await asyncio.to_thread(
            train_from_document,
            doc_name,
            final_text,
            current_user.id,
            track,
        )
    except Exception:
        logger.exception("Knowledge base training failed for '%s'", doc_name)
        raise HTTPException(
            status_code=502,
            detail="Failed to index the document into the knowledge base. Check the embedding provider and try again.",
        )

    ext_name = Path(doc_name).suffix.lower() or ".txt"
    return LearnTrainResponse(
        status="success",
        filename=doc_name,
        file_type=ext_name,
        characters_extracted=len(final_text),
        chunks_trained=chunks_count,
        track=track,
        message=f"Successfully trained knowledge base with {chunks_count} chunk(s) from '{doc_name}' (track: {track}).",
    )
