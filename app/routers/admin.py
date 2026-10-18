# /admin — user & role management. Admins assign the instructor role.
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_admin
from app.db.database import get_session
from app.db.models import User
from app.models.schemas import RoleUpdate, UserOut
from app.services import trace_store
from app.services.peppercorns import credit
from app.services.strikes import list_events, reinstate
from app.services import admin_audit
from app.models.schemas import InstructorLanguagesUpdate
from app.db.models import InstructorLanguage

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get('/languages')
async def language_catalog(_: User = Depends(require_admin)):
    from app.services.language_access import available_languages
    return {'languages': available_languages()}


@router.get('/users/{user_id}/languages')
async def teaching_languages(user_id: str, _: User = Depends(require_admin),
                             session: AsyncSession = Depends(get_session)):
    from app.services.language_access import access_view
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(404, 'User not found')
    assigned = list((await session.scalars(select(InstructorLanguage.language).where(
        InstructorLanguage.user_id == user_id))).all())
    return {**await access_view(session, user), 'assigned_languages': sorted(assigned)}


@router.put('/users/{user_id}/languages')
async def assign_languages(user_id: str, update: InstructorLanguagesUpdate,
                           admin: User = Depends(require_admin),
                           session: AsyncSession = Depends(get_session)):
    from app.services.language_access import available_languages
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(404, 'User not found')
    if user.role != 'instructor':
        raise HTTPException(409, 'Teaching languages can only be assigned to instructors.')
    languages = set(update.languages)
    if languages - set(available_languages()):
        raise HTTPException(422, 'Choose supported teaching languages.')
    previous = list((await session.scalars(select(InstructorLanguage.language).where(InstructorLanguage.user_id == user_id))).all())
    await session.execute(delete(InstructorLanguage).where(InstructorLanguage.user_id == user_id))
    session.add_all(InstructorLanguage(user_id=user_id, language=language, assigned_by=admin.id)
                    for language in sorted(languages))
    admin_audit.record(session, admin.id, 'teaching_languages', user_id,
                       before={'languages': sorted(previous)}, after={'languages': sorted(languages)})
    await session.commit()
    return await teaching_languages(user_id, admin, session)


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
    """Promote a student to instructor (or demote). An admin cannot demote
    themselves — that could lock the last admin out of the system."""
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id and update.role != "admin":
        raise HTTPException(
            status_code=400, detail="You cannot change your own admin role."
        )

    previous_role = user.role
    user.role = update.role
    admin_audit.record(session, admin.id, 'role_change', user_id,
                       before={'role': previous_role}, after={'role': update.role})
    await session.commit()
    await session.refresh(user)
    return UserOut.model_validate(user)


@router.get("/security-events")
async def security_events(
    user_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Audit trail of blocked submissions. Every automated strike must be
    reviewable by a human — that is what makes suspension defensible."""
    events = await list_events(session, user_id, limit=limit, offset=offset)
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
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Clears a suspension and resets the strike counter. The security_events
    rows are retained deliberately, so the history survives the reversal."""
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    previous = {'status': user.status, 'strikes': user.strikes}
    await reinstate(session, user)
    admin_audit.record(session, admin.id, 'account_reinstated', user_id, before=previous,
                       after={'status': user.status, 'strikes': user.strikes})
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
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Retention is manual by design — traces grow quickly and the right
    policy depends on how much history you want to debug against."""
    if older_than_days < 1:
        raise HTTPException(422, 'Retention must be at least one day.')
    removed = await trace_store.prune(session, older_than_days, commit=False)
    admin_audit.record(session, admin.id, 'traces_pruned', 'trace_records',
                       after={'older_than_days': older_than_days, 'removed': removed})
    await session.commit()
    return {"deleted": removed, "older_than_days": older_than_days}


@router.post("/users/{user_id}/peppercorns", response_model=UserOut)
async def grant_peppercorns(
    user_id: str,
    amount: int,
    reason: str = "admin_grant",
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
    idempotency_key: str | None = Header(default=None),
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

    from app.services.operations import perform
    async def work(_):
        balance = await credit(session, user_id, amount, reason=f"admin:{reason}")
        admin_audit.record(session, admin.id, 'peppercorn_grant', user_id, reason=reason[:500],
                           before={'peppercorns': balance-amount}, after={'peppercorns': balance, 'amount': amount})
        await session.refresh(target)
        return UserOut.model_validate(target)
    return await perform(session, admin.id, "admin:credit", idempotency_key,
                         {"user_id": user_id, "amount": amount, "reason": reason},
                         0, "admin:credit", work)
