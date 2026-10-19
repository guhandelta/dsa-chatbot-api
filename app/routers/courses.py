"""Learning courses drawn from curated sources, separate from authoring tools."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import User
from app.services.language_access import allowed_languages, require_language

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/")
async def courses(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    from app.services.course_catalog import list_courses
    languages = await allowed_languages(session, user)
    return {"courses": [course for course in list_courses() if course["language"] in languages]}


@router.get("/{language}")
async def course(language: str, user: User = Depends(get_current_user),
                 session: AsyncSession = Depends(get_session)):
    from app.services.course_catalog import get_course
    await require_language(session, user, language)
    result = get_course(language)
    if result is None:
        raise HTTPException(404, "No course outline has been authored for this language yet.")
    return result


@router.get("/{language}/modules/{module_id}/sources/{source_id}")
async def lesson(language: str, module_id: str, source_id: str,
                 user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    from app.services.course_catalog import get_lesson
    await require_language(session, user, language)
    result = get_lesson(language, module_id, source_id)
    if result is None:
        raise HTTPException(404, "That reading is not available in this course module.")
    return result
