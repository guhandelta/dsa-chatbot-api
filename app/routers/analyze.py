# /analyze — submit code for review.
#
# Pipeline (deterministic, not an agent loop):
#   1. account check  — suspended accounts are refused outright
#   2. static screen  — malicious patterns blocked BEFORE execution; a hard
#                       block records a strike
#   3. debit          — atomic, before any expensive work
#   4. execute        — run against the problem's verified test cases so
#                       feedback is grounded in evidence, not opinion
#   5. LLM review     — given the real pass/fail results
#   6. refund         — on any infrastructure failure
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import User
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.code_screener import explain, screen
from app.services import learning_profile
from app.services.content_catalog import filter_content
from app.services.deep_review import deep_review
from app.services import trace_store
from app.services.tracing import trace
from app.services.peppercorns import InsufficientPeppercornsError, credit, debit
from app.services.rate_limit import RateLimitExceeded, enforce_rate_limit
from app.services.strikes import AccountSuspendedError, assert_active, record_event

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("/", response_model=AnalyzeResponse)
async def analyze(
    request: AnalyzeRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # --- 1. suspended accounts cannot submit ---------------------------
    try:
        assert_active(current_user)
    except AccountSuspendedError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    # --- 2. static screen BEFORE spending peppercorns or a process -----
    verdict = screen(request.user_code, request.language)
    if not verdict.allowed:
        outcome = await record_event(
            session, current_user, verdict, request.user_code, context="analyze"
        )
        await session.commit()
        # No debit happened, so nothing to refund — the submission never ran.
        detail = explain(verdict)
        if outcome.get("message"):
            detail = f"{detail} {outcome['message']}"
        raise HTTPException(
            status_code=403 if outcome.get("suspended") else 400,
            detail=detail,
        )

    # --- 2b. rate limit --------------------------------------------------
    # A review runs the sandbox and two LLM calls. Unbounded submission is a
    # cost and CPU exposure even from a well-meaning client with a retry bug.
    try:
        await enforce_rate_limit(session, current_user.id, kind="attempt")
    except RateLimitExceeded as exc:
        raise HTTPException(status_code=429, detail=str(exc))

    # --- 3. debit atomically -------------------------------------------
    try:
        balance = await debit(
            session, current_user.id, settings.analyze_cost, reason="analyze"
        )
    except InsufficientPeppercornsError as exc:
        raise HTTPException(status_code=402, detail=str(exc))
    await session.commit()

    # --- 4/5. precision pipeline: evidence, review, self-critique -------
    # Curated cases, then differential fuzzing against the verified reference,
    # then measured complexity, then review, then an audit pass that strips
    # any claim the evidence does not support.
    # One trace per review. Stage spans inside deep_review attach to it, so
    # "which stage was slow / expensive / failing" is answerable afterwards.
    try:
        async with trace(
            "analyze",
            user_id=current_user.id,
            problem_id=request.problem_id,
            language=request.language,
            provider=request.provider,
        ) as t:
            analysis, evidence = await deep_review(
                problem_id=request.problem_id,
                user_code=request.user_code,
                language=request.language,
                provider=request.provider,
            )
            execution = evidence.get("curated")
        await trace_store.save(session, t)
    except Exception:
        logger.exception(
            "Analysis failed; refunding %s peppercorns", settings.analyze_cost
        )
        balance = await credit(
            session, current_user.id, settings.analyze_cost, reason="refund:analyze"
        )
        await session.commit()
        raise HTTPException(
            status_code=502,
            detail="The AI provider failed to analyze your code. Your peppercorns were refunded.",
        )

    # --- 6. record the attempt so the mentor can learn their patterns -----
    # Without this the learning profile stays empty and tier-3 recall never
    # fires — the mentor would be reading a table nothing writes to.
    algorithms: list[str] = []
    for c in filter_content():
        if c.id == request.problem_id:
            algorithms = c.algorithms
            break

    category, detail = learning_profile.categorize_failure(evidence)
    fuzz = (evidence or {}).get("fuzz") or {}
    curated_ok = True
    for r in ((evidence or {}).get("curated") or {}).get("results", []):
        if r.get("tier") == 1 and r.get("status") != "passed":
            curated_ok = False
    solved = curated_ok and not category and not fuzz.get("counterexamples")

    await learning_profile.record_event(
        session,
        current_user.id,
        request.problem_id,
        kind="solved" if solved else "attempt",
        language=request.language,
        algorithms=algorithms,
        error_category=category,
        detail=detail,
    )
    await session.commit()

    return AnalyzeResponse(
        analysis=analysis,
        peppercorns_remaining=balance,
        execution=json.loads(json.dumps(execution)) if execution else None,
        evidence=json.loads(json.dumps(evidence, default=str)),
    )
