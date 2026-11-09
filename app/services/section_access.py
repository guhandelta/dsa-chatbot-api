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


async def compare_access(session, user, section: str, language: str) -> dict[str, object]:
    """Report the legacy and candidate decisions without changing either policy.

    This is for an offline migration audit. Do not expose its result to learners:
    the candidate can be denied solely because grants have not been issued yet.
    """
    if section not in SECTIONS:
        raise ValueError(f"Unknown learning section: {section}")
    try:
        await require_language(session, user, language)
    except HTTPException:
        return {"section": section, "language": language, "legacy_allows": False,
                "candidate_allows": False, "differs": False}
    try:
        await require_section(session, user, section, language)
    except HTTPException:
        candidate_allows = False
    else:
        candidate_allows = True
    return {"section": section, "language": language, "legacy_allows": True,
            "candidate_allows": candidate_allows, "differs": not candidate_allows}
