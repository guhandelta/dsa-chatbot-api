# /mentor — Socratic guidance. Requires a subscription for the language the
# learner is coding in. Tiers 1-2 are free on every problem; 3-4 cost peppercorns.
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import LearningEvent, User
from app.models.schemas import MentorRequest, MentorResponse
from app.services import entitlements, learning_profile, trace_store
from app.services.tracing import span, trace
from app.services.content_catalog import filter_content
from app.services.mentor import MAX_TIER, TIERS, hint_cost, mentor_reply, pricing, step_back_offer
from app.services.peppercorns import InsufficientPeppercornsError, credit, debit
from app.services.rate_limit import RateLimitExceeded, enforce_rate_limit
from app.services.strikes import AccountSuspendedError, assert_active

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mentor", tags=["mentor"])


def _algorithms_for(problem_id: str) -> list[str]:
    for c in filter_content():
        if c.id == problem_id:
            return c.algorithms
    return []


async def _current_tier(session: AsyncSession, user_id: str, problem_id: str,
                        language: str = "python", *, now: datetime | None = None) -> int:
    """Fixed six-week cycles anchored to the first hint for this scope.

    A new session, subscription renewal, or recent hint never shifts the reset.
    Language switching has its own hint history. Timestamps are interpreted in UTC.
    """
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    times = list((await session.scalars(select(LearningEvent.created_at).where(
        LearningEvent.user_id == user_id,
        LearningEvent.problem_id == problem_id,
        LearningEvent.language == language,
        LearningEvent.kind == "hint",
        LearningEvent.created_at <= now,
    ).order_by(LearningEvent.created_at))).all())
    if not times:
        return 1
    times = [t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t for t in times]
    duration = timedelta(hours=settings.hint_tier_reset_hours)
    anchor = times[0]
    cycle_start = anchor + ((now - anchor) // duration) * duration
    return min(sum(t >= cycle_start for t in times) + 1, MAX_TIER)


@router.get("/entitlement")
async def entitlement(
    language: str = "python",
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await entitlements.check(session, current_user.id, language)


@router.post("/ask", response_model=MentorResponse)
async def ask(request: MentorRequest, current_user: User = Depends(get_current_user),
              session: AsyncSession = Depends(get_session),
              idempotency_key: str | None = Header(default=None)):
    from app.services.operations import perform
    from app.services.content_catalog import content_exists
    try:
        assert_active(current_user)
    except AccountSuspendedError as exc:
        raise HTTPException(403,str(exc))
    if not content_exists(request.problem_id):
        raise HTTPException(404,'Problem not found')
    from app.services.language_access import require_content
    await require_content(session, current_user, request.problem_id, request.language)
    async def prepare():
        decision=await entitlements.check(session,current_user.id,request.language)
        if not decision['entitled']:
            raise HTTPException(402,decision['reason'])
        try:
            await enforce_rate_limit(session,current_user.id,'hint')
        except RateLimitExceeded as exc:
            raise HTTPException(429,str(exc))
    tier=1
    async def price(_operation):
        # Under the per-user lock, so the charged tier matches the one served.
        nonlocal tier
        tier=await _current_tier(session,current_user.id,request.problem_id,request.language)
        return hint_cost(tier)
    async def work(balance):
        from app.services.operations import current_balance
        algorithms=_algorithms_for(request.problem_id)
        recalled=await learning_profile.recall_similar_moment(session,current_user.id,algorithms,request.problem_id,request.language)
        profile=await learning_profile.build_profile(session,current_user.id)
        async with trace('mentor',user_id=current_user.id,problem_id=request.problem_id,language=request.language,tier=tier) as t:
            reply=await mentor_reply(problem_id=request.problem_id,reasoning=request.reasoning,
                current_code=request.current_code,language=request.language,tier=tier,provider=request.provider,
                recalled_moment=recalled,profile_summary=profile.summary() if profile.total_attempts else '')
        await trace_store.save(session,t)
        await learning_profile.record_event(session,current_user.id,request.problem_id,kind='hint',
            language=request.language,algorithms=algorithms,hint_tier=tier,reasoning=request.reasoning)
        return MentorResponse(reply=reply,hint_tier=tier,tier_label=TIERS[tier][0],
            recalled_moment=recalled,step_back_offer=step_back_offer(request.problem_id,algorithms) if tier>=MAX_TIER else None,
            peppercorns_remaining=balance if balance is not None else await current_balance(session,current_user.id),
            peppercorns_charged=hint_cost(tier),next_hint_cost=hint_cost(min(tier+1,MAX_TIER)))
    return await perform(session,current_user.id,'mentor',idempotency_key,request.model_dump(),
                         price,'mentor',work,prepare=prepare)


@router.get("/next-hint")
async def next_hint(
    problem_id: str,
    language: str = "python",
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """The tier and price of the learner's next hint on this problem."""
    from app.services.language_access import require_content
    await require_content(session, current_user, problem_id, language)
    return pricing(await _current_tier(session, current_user.id, problem_id, language))


@router.post("/reflect")
async def reflect(
    problem_id: str,
    reasoning: str,
    language: str = "python",
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Record how the learner reasoned through a problem they solved.

    Free (no peppercorns): this is the raw material tier-3 recall draws on,
    so charging for it would starve the feature that makes the mentor good.
    """
    try:
        assert_active(current_user)
    except AccountSuspendedError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    from app.services.content_catalog import content_exists
    from app.services.language_access import require_content
    await require_content(session, current_user, problem_id, language)
    if not content_exists(problem_id):
        raise HTTPException(status_code=404, detail="Problem not found")
    if not reasoning.strip() or len(reasoning) > 4000:
        raise HTTPException(status_code=422, detail="Reflection must contain 1–4000 characters.")
    solved = await session.scalar(select(LearningEvent.id).where(
        LearningEvent.user_id == current_user.id,
        LearningEvent.problem_id == problem_id,
        LearningEvent.language == language,
        LearningEvent.kind == "solved",
    ).limit(1))
    if solved is None:
        raise HTTPException(status_code=403, detail="Pass evaluation in this language before reflecting.")
    await learning_profile.record_event(
        session,
        current_user.id,
        problem_id,
        kind="reflection",
        language=language,
        algorithms=_algorithms_for(problem_id),
        reasoning=reasoning,
    )
    await session.commit()
    return {"recorded": True}


@router.get("/profile")
async def my_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """The learner's own view of their pattern. Behavioural only."""
    profile = await learning_profile.build_profile(session, current_user.id)
    return profile.to_dict()


@router.get("/profile/export")
async def export_my_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Full export. A behavioural profile of a paying customer must be
    exportable on request."""
    return await learning_profile.export_profile(session, current_user.id)


@router.delete("/profile")
async def delete_my_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Erase learning-profile events. Saved sessions and chats are separate. Deleting it costs the learner their
    personalisation, which the UI should say plainly before calling this."""
    removed = await learning_profile.delete_profile(session, current_user.id)
    await session.commit()
    return {"deleted_events": removed}
