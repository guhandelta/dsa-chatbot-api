# /admin — user & role management. Admins assign the teacher role.
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_admin
from app.db.database import get_session
from app.db.models import User
from app.models.schemas import RoleUpdate, UserOut
from app.services import trace_store
from app.services.peppercorns import credit
from app.services.strikes import list_events, reinstate

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
async def list_users(
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    rows = (
        (await session.execute(select(User).order_by(User.created_at))).scalars().all()
    )
    return [UserOut.model_validate(u) for u in rows]


@router.patch("/users/{user_id}/role", response_model=UserOut)
async def set_role(
    user_id: str,
    update: RoleUpdate,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Promote a student to teacher (or demote). An admin cannot demote
    themselves — that could lock the last admin out of the system."""
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id and update.role != "admin":
        raise HTTPException(
            status_code=400, detail="You cannot change your own admin role."
        )

    user.role = update.role
    await session.commit()
    await session.refresh(user)
    return UserOut.model_validate(user)


@router.get("/security-events")
async def security_events(
    user_id: str | None = None,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Audit trail of blocked submissions. Every automated strike must be
    reviewable by a human — that is what makes suspension defensible."""
    events = await list_events(session, user_id)
    return [
        {
            "id": e.id,
            "user_id": e.user_id,
            "severity": e.severity,
            "reasons": e.reasons,
            "context": e.context,
            "counted_as_strike": e.counted_as_strike,
            "created_at": e.created_at.isoformat(),
            "code_excerpt": e.code_excerpt[:500],
        }
        for e in events
    ]


@router.post("/users/{user_id}/reinstate", response_model=UserOut)
async def reinstate_user(
    user_id: str,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Clears a suspension and resets the strike counter. The security_events
    rows are retained deliberately, so the history survives the reversal."""
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await reinstate(session, user)
    await session.commit()
    await session.refresh(user)
    return UserOut.model_validate(user)


# ---------------- observability ----------------


@router.get("/traces")
async def list_traces(
    limit: int = 50,
    name: str | None = None,
    status: str | None = None,
    user_id: str | None = None,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Recent traces, newest first. Filter by operation name ("analyze",
    "mentor"), status ("error"), or user."""
    return await trace_store.recent(
        session, limit=limit, name=name, status=status, user_id=user_id
    )


@router.get("/traces/summary")
async def trace_summary(
    limit: int = 500,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Aggregates over recent traces: call counts, error rate, avg and p95
    latency, average cost, and a per-stage breakdown showing where the time
    actually goes. This is the view that answers "why is review slow?"."""
    return await trace_store.summary(session, limit=limit)


@router.get("/traces/{trace_id}")
async def trace_detail(
    trace_id: str,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """The full span tree for one request."""
    payload = await trace_store.detail(session, trace_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Trace not found")
    return payload


@router.delete("/traces")
async def prune_traces(
    older_than_days: int = 14,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Retention is manual by design — traces grow quickly and the right
    policy depends on how much history you want to debug against."""
    removed = await trace_store.prune(session, older_than_days)
    return {"deleted": removed, "older_than_days": older_than_days}


@router.post("/users/{user_id}/peppercorns", response_model=UserOut)
async def grant_peppercorns(
    user_id: str,
    amount: int,
    reason: str = "admin_grant",
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Credit peppercorns to an account.

    For support situations — comping a user after an outage, correcting a
    failed refund. Goes through `credit()` rather than setting the balance
    directly, so the transaction ledger stays reconcilable with the balance.
    """
    target = await session.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    await credit(session, user_id, amount, reason=f"admin:{reason}")
    await session.commit()
    await session.refresh(target)
    return UserOut.model_validate(target)
