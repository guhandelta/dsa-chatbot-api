# /mentor — Socratic guidance. Requires a subscription for the language the
# learner is coding in, and costs peppercorns per turn.
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
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
from app.services.mentor import MAX_TIER, TIERS, mentor_reply, step_back_offer
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


async def _current_tier(session: AsyncSession, user_id: str, problem_id: str) -> int:
    """Hint tier for this learner on this problem.

    Escalation is driven by the learner asking again within one working
    session — never volunteered, and never permanent. Hints older than
    `hint_tier_reset_hours` are ignored, so a learner returning to a problem
    days later starts at tier 1 and gets to think it through again rather
    than being handed the strongest hint immediately.

    Without the window, tier only ever ratchets upward: come back next week
    and the mentor opens by naming the technique, which defeats the point.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(
        hours=settings.hint_tier_reset_hours
    )
    stmt = select(LearningEvent).where(
        LearningEvent.user_id == user_id,
        LearningEvent.problem_id == problem_id,
        LearningEvent.kind == "hint",
        LearningEvent.created_at >= cutoff,
    )
    hints = list((await session.execute(stmt)).scalars())
    return min(len(hints) + 1, MAX_TIER)


@router.get("/entitlement")
async def entitlement(
    language: str = "python",
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await entitlements.check(session, current_user.id, language)


@router.post("/ask", response_model=MentorResponse)
async def ask(
    request: MentorRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        assert_active(current_user)
    except AccountSuspendedError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    # Gate 1: subscription for this language unlocks the mentor
    decision = await entitlements.check(session, current_user.id, request.language)
    if not decision["entitled"]:
        raise HTTPException(status_code=402, detail=decision["reason"])

    # Gate 2: rate limit — mentor turns are LLM calls, so an unbounded
    # client loop is a direct cost exposure.
    try:
        await enforce_rate_limit(session, current_user.id, kind="hint")
    except RateLimitExceeded as exc:
        raise HTTPException(status_code=429, detail=str(exc))

    # Gate 3: peppercorns still pay for the turn
    try:
        balance = await debit(
            session, current_user.id, settings.mentor_cost, reason="mentor"
        )
    except InsufficientPeppercornsError as exc:
        raise HTTPException(status_code=402, detail=str(exc))
    await session.commit()

    algorithms = _algorithms_for(request.problem_id)
    tier = await _current_tier(session, current_user.id, request.problem_id)

    # The strongest hint available: their own earlier reasoning on a
    # structurally similar problem.
    recalled = await learning_profile.recall_similar_moment(
        session, current_user.id, algorithms, request.problem_id
    )
    profile = await learning_profile.build_profile(session, current_user.id)

    try:
        async with trace(
            "mentor",
            user_id=current_user.id,
            problem_id=request.problem_id,
            language=request.language,
            tier=tier,
        ) as t:
            async with span("recall_lookup") as sp:
                sp.set(found=bool(recalled), algorithms=algorithms)
            async with span("llm_mentor", provider=request.provider):
                reply = await mentor_reply(
                    problem_id=request.problem_id,
                    reasoning=request.reasoning,
                    current_code=request.current_code,
                    language=request.language,
                    tier=tier,
                    provider=request.provider,
                    recalled_moment=recalled,
                    profile_summary=profile.summary() if profile.total_attempts else "",
                )
        await trace_store.save(session, t)
    except Exception:
        logger.exception("Mentor failed; refunding")
        balance = await credit(
            session, current_user.id, settings.mentor_cost, reason="refund:mentor"
        )
        await session.commit()
        raise HTTPException(
            status_code=502,
            detail="The mentor could not respond. Your peppercorns were refunded.",
        )

    # Record the learner's own words — this becomes the raw material for
    # reminding them how they think, on a later problem.
    await learning_profile.record_event(
        session,
        current_user.id,
        request.problem_id,
        kind="hint",
        language=request.language,
        algorithms=algorithms,
        hint_tier=tier,
        reasoning=request.reasoning,
    )
    await session.commit()

    offer = (
        step_back_offer(request.problem_id, algorithms) if tier >= MAX_TIER else None
    )

    return MentorResponse(
        reply=reply,
        hint_tier=tier,
        tier_label=TIERS[tier][0],
        recalled_moment=recalled,
        step_back_offer=offer,
        peppercorns_remaining=balance,
    )


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
    await learning_profile.record_event(
        session,
        current_user.id,
        problem_id,
        kind="solved",
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
    """Erase all learning history. Deleting it costs the learner their
    personalisation, which the UI should say plainly before calling this."""
    removed = await learning_profile.delete_profile(session, current_user.id)
    await session.commit()
    return {"deleted_events": removed}
