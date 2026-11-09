"""Student-authored pathway notes; no planner or mastery side effects."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import StudentPathRecord, User
from app.services.concept_links import pilot
from app.services.language_access import require_language

router = APIRouter(prefix="/learning-records", tags=["learning-records"])
Section = Literal["language", "dsa", "design-patterns"]
Kind = Literal["goal", "assumption", "decision", "path_request"]


class RecordCreate(BaseModel):
    section: Section
    language: str = Field(min_length=1, max_length=32)
    kind: Kind
    concept_id: str | None = Field(default=None, max_length=120)
    body: str = Field(min_length=1, max_length=2000)

    @field_validator("body")
    @classmethod
    def nonblank_body(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Body cannot be blank")
        return value


def view(row: StudentPathRecord) -> dict:
    return {"id": row.id, "section": row.section, "language": row.language,
            "kind": row.kind, "concept_id": row.concept_id or None, "body": row.body,
            "curriculum_version": row.curriculum_version, "created_at": row.created_at}


@router.post("/", status_code=201)
async def create(request: RecordCreate, user: User = Depends(get_current_user),
                 session: AsyncSession = Depends(get_session)):
    await require_language(session, user, request.language)
    concept_id = request.concept_id or ""
    graph = pilot()
    if concept_id:
        matches = {node["id"]: node for node in graph["nodes"]}
        node = matches.get(concept_id)
        if not node or node["section"] != request.section:
            raise HTTPException(422, "Concept is not in this section's pilot map.")
        if request.section == "language" and not concept_id.startswith(f"language:{request.language}:"):
            raise HTTPException(422, "Concept is not in the selected language.")
        if request.section == "design-patterns" and not concept_id.endswith(f":{request.language}"):
            raise HTTPException(422, "Concept is not in the selected language.")
    elif request.kind in ("assumption", "decision"):
        raise HTTPException(422, "Assumptions and decisions need a concept ID.")
    row = StudentPathRecord(user_id=user.id, section=request.section, language=request.language,
                            kind=request.kind, concept_id=concept_id, body=request.body,
                            curriculum_version=graph["version"])
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return view(row)


@router.get("/")
async def list_records(section: Section, language: str, limit: int = 50,
                       user: User = Depends(get_current_user),
                       session: AsyncSession = Depends(get_session)):
    if user.status != "active":
        raise HTTPException(403, "This account is suspended.")
    if not 1 <= limit <= 100:
        raise HTTPException(422, "Limit must be between 1 and 100.")
    rows = (await session.scalars(select(StudentPathRecord).where(
        StudentPathRecord.user_id == user.id, StudentPathRecord.section == section,
        StudentPathRecord.language == language).order_by(
        StudentPathRecord.created_at.desc(), StudentPathRecord.id.desc()).limit(limit))).all()
    return {"items": [view(row) for row in rows]}
