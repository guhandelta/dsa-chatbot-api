"""Learning strikes and extra practice. See app/services/learning_strikes.py."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import User
from app.services import learning_strikes
from app.services.language_access import resolve_language
from app.services.strikes import AccountSuspendedError, assert_active

router = APIRouter(prefix="/strikes", tags=["strikes"])


class AnswerBody(BaseModel):
    item_id: str = Field(min_length=1, max_length=200)
    response: str | int = ""


class ExtraBody(BaseModel):
    language: str = Field(min_length=1, max_length=32)
    problem_id: str = Field(default="", max_length=120)
    node_id: str = Field(default="", max_length=120)
    count: int = Field(default=3, ge=2, le=3)


def _active(user: User):
    try:
        assert_active(user)
    except AccountSuspendedError as exc:
        raise HTTPException(403, str(exc))


@router.get("")
async def overview(language: str, user: User = Depends(get_current_user),
                   session: AsyncSession = Depends(get_session)):
    _active(user)
    language = await resolve_language(session, user, language)
    return await learning_strikes.overview(session, user, language)


@router.get("/sets/{set_id}")
async def read_set(set_id: str, user: User = Depends(get_current_user),
                   session: AsyncSession = Depends(get_session)):
    _active(user)
    return await learning_strikes.set_view(session, await learning_strikes.owned_set(session, user, set_id))


@router.post("/sets/{set_id}/answers")
async def answer(set_id: str, body: AnswerBody, user: User = Depends(get_current_user),
                 session: AsyncSession = Depends(get_session)):
    _active(user)
    item_set = await learning_strikes.owned_set(session, user, set_id)
    await resolve_language(session, user, item_set.language)
    return await learning_strikes.answer(session, user, set_id, body.item_id, body.response)


@router.post("/practice")
async def extra_practice(body: ExtraBody, user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_session)):
    """Extra questions on a topic, requested by the learner, strikes or not."""
    _active(user)
    language = await resolve_language(session, user, body.language)
    return await learning_strikes.start_extra(session, user, language, body.problem_id, body.node_id, body.count)
