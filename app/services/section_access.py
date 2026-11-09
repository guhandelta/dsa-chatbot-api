"""Candidate section-access decisions; not yet wired to learning endpoints."""

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select

from app.db.models import SectionEntitlement
from app.services.content_catalog import SECTIONS
from app.services.language_access import require_language


def _aware(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


async def require_section(session, user, section: str, language: str, *, now: datetime | None = None) -> str:
    """Check both axes when section enforcement is eventually activated."""
    if section not in SECTIONS:
        raise HTTPException(404, "Unknown learning section.")
    await require_language(session, user, language)
    if user.role in ("admin", "instructor"):
        return section
    # require_language has already rejected roles without student/staff scope.
    moment = _aware(now or datetime.now(timezone.utc))
    rows = (await session.scalars(select(SectionEntitlement).where(
        SectionEntitlement.user_id == user.id,
        SectionEntitlement.section == section,
        SectionEntitlement.status == "active"))).all()
    if any(_aware(row.starts_at) <= moment < _aware(row.expires_at) for row in rows):
        return section
    raise HTTPException(403, "An active entitlement for this learning section is required.")
