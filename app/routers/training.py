# /training — instructor & admin only. Submit a problem, get it reviewed,
# corrected, completed in all six languages, executed, and auto-published
# if (and only if) every check passes.
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_instructor
from app.db.database import get_session
from app.db.models import Submission, User
from app.models.schemas import TrainRequest
from app.services.code_runner import available_languages
from app.services.knowledge_base import delete_problem
from app.services.problem_catalog import PROBLEMS_DIR, list_problems, problem_exists
from app.services.training_pipeline import run_pipeline, submission_payload

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/training", tags=["training"])


@router.get("/status")
async def training_status(user: User = Depends(require_instructor)):
    """What this environment can actually verify — the UI shows this so an
    instructor knows up front which languages will be executed."""
    tools = available_languages()
    return {
        "role": user.role,
        "toolchains": tools,
        "executed_languages": [l for l in ("python", "javascript") if tools.get(l)],
        "compiled_languages": [l for l in ("c", "cpp", "java", "rust") if tools.get(l)],
        "unavailable": [l for l, ok in tools.items() if not ok],
        "note": "Languages without a toolchain are reported as 'unverified' and "
                "never counted as passing. Install javac/rustc to verify Java and Rust.",
    }


@router.post("/submit")
async def submit_problem(
    request: TrainRequest,
    user: User = Depends(require_instructor),
    session: AsyncSession = Depends(get_session),
):
    """Runs the full pipeline. Publishing is automatic only when every
    executable check passes; otherwise the draft is stored for review."""
    if problem_exists(request.problem_id):
        raise HTTPException(
            status_code=409,
            detail=f"'{request.problem_id}' already exists. Delete it first to retrain.",
        )

    try:
        result = await run_pipeline(
            problem_id=request.problem_id,
            problem_hint=request.problem,
            supplied=request.solutions,
            provider=request.provider,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Training pipeline failed")
        raise HTTPException(status_code=502, detail=f"Training pipeline failed: {exc}")

    session.add(
        Submission(
            user_id=user.id,
            problem_id=request.problem_id,
            status=result["status"],
            raw_input=submission_payload(request.problem, request.solutions),
            report_json=json.dumps(
                {k: v for k, v in result.items() if k != "markdown"}, default=str
            ),
            markdown=result["markdown"],
        )
    )
    await session.commit()
    return result


@router.get("/submissions")
async def list_submissions(
    user: User = Depends(require_instructor),
    session: AsyncSession = Depends(get_session),
):
    """Admins see everything; instructors see their own submissions."""
    stmt = select(Submission).order_by(Submission.created_at.desc())
    if user.role != "admin":
        stmt = stmt.where(Submission.user_id == user.id)
    rows = (await session.execute(stmt)).scalars().all()
    return [
        {
            "id": s.id,
            "problem_id": s.problem_id,
            "status": s.status,
            "created_at": s.created_at.isoformat(),
            "report": json.loads(s.report_json),
        }
        for s in rows
    ]


@router.delete("/problems/{problem_id}")
async def remove_problem(problem_id: str, user: User = Depends(require_instructor)):
    """Removes a problem from the knowledge base (file + vector chunks),
    so it can be retrained from scratch."""
    path = PROBLEMS_DIR / f"{problem_id}.md"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Problem not found")
    path.unlink()
    delete_problem(problem_id)
    list_problems.cache_clear()
    return {"deleted": problem_id}
