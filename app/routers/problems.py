"""Problem statements are public; solutions require an evaluated submission."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import User
from app.services.problem_catalog import ProblemMeta, list_problems
from app.services.content_catalog import content_exists
from app.services.content_verification import require_verified_reference
from app.services.content_access import can_reveal, learner_document, solution_document

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("/", response_model=list[ProblemMeta])
def get_problems():
    return list_problems()


@router.get("/{problem_id}")
def get_problem(problem_id: str):
    if not content_exists(problem_id):
        raise HTTPException(status_code=404, detail="Problem not found")
    return {"id": problem_id, "markdown": learner_document(problem_id)}


@router.get("/{problem_id}/solution-access")
async def solution_access(problem_id: str, language: str,
                          user: User = Depends(get_current_user),
                          session: AsyncSession = Depends(get_session)):
    if not content_exists(problem_id):
        raise HTTPException(status_code=404, detail="Problem not found")
    return {"available": bool(solution_document(problem_id, language)) and
            await can_reveal(session, user.id, problem_id, language)}


@router.get("/{problem_id}/solution")
async def reveal_solution(problem_id: str, language: str,
                          user: User = Depends(get_current_user),
                          session: AsyncSession = Depends(get_session)):
    if not content_exists(problem_id):
        raise HTTPException(status_code=404, detail="Problem not found")
    if not await can_reveal(session, user.id, problem_id, language):
        raise HTTPException(status_code=403, detail="Submit code and complete evaluation in this language before revealing the solution.")
    markdown = solution_document(problem_id, language)
    if not markdown:
        raise HTTPException(status_code=404, detail="No solution is available in this language.")
    await require_verified_reference(problem_id, language)
    return {"id": problem_id, "language": language, "markdown": markdown}
