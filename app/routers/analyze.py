"""Execution-grounded review with durable request receipts."""
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import User
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services import learning_profile, trace_store
from app.services.code_screener import explain, screen
from app.services.content_catalog import content_exists, filter_content
from app.services.content_access import evaluation_completed
from app.services.content_verification import require_verified_reference
from app.services.deep_review import deep_review
from app.services.operations import perform
from app.services.rate_limit import RateLimitExceeded, enforce_rate_limit
from app.services.strikes import AccountSuspendedError, assert_active, record_event
from app.services.tracing import trace

router=APIRouter(prefix='/analyze',tags=['analyze'])


async def screen_submission(session,user,code,language,context='analyze'):
    verdict=screen(code,language)
    if not verdict.allowed:
        outcome=await record_event(session,user,verdict,code,context=context)
        await session.commit()
        raise HTTPException(403 if outcome.get('suspended') else 400,
                            explain(verdict)+' '+outcome.get('message',''))


async def check_submission(session,user,code,language):
    await screen_submission(session,user,code,language)
    try:
        await enforce_rate_limit(session,user.id,'attempt')
    except RateLimitExceeded as exc:
        raise HTTPException(429,str(exc))


def validate_problem(problem_id,language):
    if not content_exists(problem_id):
        raise HTTPException(404,'Problem not found')
    item=next((c for c in filter_content() if c.id==problem_id),None)
    if item and item.language and item.language!=language:
        raise HTTPException(400,'Choose the exercise language before submitting.')


async def save_evaluation(session,user_id,problem_id,language,evidence,rewards_out=None,strikes_out=None,
                          practice_session_id=None):
    from app.services.user_lock import lock_user
    await lock_user(session, user_id)
    from app.graphs.practice import classify_outcome
    algorithms=next((c.algorithms for c in filter_content() if c.id==problem_id),[])
    outcome,category,detail=classify_outcome(evidence)
    from app.services import rewards
    completed=evaluation_completed(evidence or {},language)
    solved=completed and outcome=='passed'
    first_solve=solved and not await rewards.has_solved(session,user_id,problem_id,language)
    if completed:
        await learning_profile.record_event(session,user_id,problem_id,kind='evaluated',language=language,algorithms=algorithms,
                                            practice_session_id=practice_session_id)
    await learning_profile.record_event(session,user_id,problem_id,
        kind='solved' if solved else 'attempt',language=language,
        algorithms=algorithms,error_category=category,detail=detail,
        practice_session_id=practice_session_id)
    earned=await rewards.after_solve(session,user_id,problem_id,language,first_solve=first_solve) if solved else []
    if completed and not solved:
        # Only a completed paid evaluation earns a learning strike.
        from app.services.learning_strikes import record_failed_evaluation,strike_view
        strike=await record_failed_evaluation(session,user_id,problem_id,language,evidence,category)
        if strike is not None and strikes_out is not None:
            strikes_out.append(await strike_view(session,strike))
    if rewards_out is not None:
        rewards_out.extend(earned)
    return completed


@router.post('/',response_model=AnalyzeResponse)
async def analyze(request:AnalyzeRequest,current_user:User=Depends(get_current_user),
                  session:AsyncSession=Depends(get_session),
                  idempotency_key:str|None=Header(default=None)):
    try: assert_active(current_user)
    except AccountSuspendedError as exc: raise HTTPException(403,str(exc))
    validate_problem(request.problem_id,request.language)
    from app.services.language_access import require_content
    await require_content(session, current_user, request.problem_id, request.language)
    async def prepare():
        from app.services.learning_strikes import require_no_blocking
        await require_no_blocking(session, current_user.id, request.language, request.problem_id)
        await require_verified_reference(request.problem_id,request.language)
        await check_submission(session,current_user,request.user_code,request.language)
    async def work(balance):
        algorithms=next((c.algorithms for c in filter_content() if c.id==request.problem_id),[])
        recalled=await learning_profile.recall_similar_moment(session,current_user.id,algorithms,request.problem_id,request.language)
        async with trace('analyze',user_id=current_user.id,problem_id=request.problem_id,
                         language=request.language,provider=request.provider) as t:
            analysis,evidence=await deep_review(problem_id=request.problem_id,user_code=request.user_code,
                language=request.language,provider=request.provider,
                **({"recalled_moment": recalled} if recalled else {}))
        await trace_store.save(session,t)
        earned=[]
        completed=await save_evaluation(session,current_user.id,request.problem_id,request.language,evidence,earned)
        from app.services.content_access import can_reveal
        available=completed and await can_reveal(session,current_user.id,request.problem_id,request.language)
        if earned:
            balance=earned[-1]['balance']
        return AnalyzeResponse(analysis=analysis,peppercorns_remaining=balance,rewards=earned,
            execution=evidence.get('curated'),evidence=evidence,solution_available=available)
    return await perform(session,current_user.id,'analyze',idempotency_key,request.model_dump(),
                         settings.analyze_cost,'analyze',work,prepare=prepare)
