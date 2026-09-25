# /problems endpoint — public catalog so the frontend can populate a picker.
from fastapi import APIRouter, HTTPException

from app.services.problem_catalog import ProblemMeta, list_problems, read_problem_doc

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("/", response_model=list[ProblemMeta])
def get_problems():
    return list_problems()


@router.get("/{problem_id}")
def get_problem(problem_id: str):
    """Returns the raw markdown for a single problem (description, hints,
    approach, and reference solutions in all languages)."""
    doc = read_problem_doc(problem_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Problem not found")
    return {"id": problem_id, "markdown": doc}
