"""Authenticated, durable LangGraph practice sessions. Billing stays outside nodes."""
from fastapi import APIRouter,Depends,Header,HTTPException
from pydantic import BaseModel,Field
from typing import Literal
from sqlalchemy import select,update
from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.types import Command
from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import PracticeSession,User,LearningEvent
from app.graphs.practice import build_practice_graph,default_deps,pending_interrupt,thread_config
from app.models.schemas import Provider
from app.routers.analyze import check_submission,save_evaluation,validate_problem
from app.routers.mentor import _current_tier,_algorithms_for
from app.services import entitlements,learning_profile
from app.services.content_verification import require_verified_reference
from app.services.evidence_safety import learner_safe
from app.services.operations import perform,recover_expired_scope
from app.services.practice_checkpoints import TransactionalSaver
from app.services.strikes import assert_active,AccountSuspendedError
from app.services.rate_limit import enforce_rate_limit,RateLimitExceeded
from app.services.language_access import require_content

router=APIRouter(prefix='/practice',tags=['practice'])

class StartRequest(BaseModel):
    problem_id:str=Field(min_length=1,max_length=120)
    language:str
    provider:Provider='gemini'

class WorkspaceFile(BaseModel):
    name:str=Field(min_length=1,max_length=64)
    content:str=Field(default='',max_length=20000)

class ActionRequest(BaseModel):
    action:Literal['submit','hint','reflect','quit']
    code:str=Field(default='',max_length=20000)
    # A multi-file workspace; bundled server-side into `code` for submit and hint.
    files:list[WorkspaceFile]|None=Field(default=None,max_length=8)
    entry:str|None=Field(default=None,max_length=64)
    reasoning:str=Field(default='',max_length=4000)
    max_hint_cost:int|None=Field(default=None,ge=0)


def active(user):
    try:assert_active(user)
    except AccountSuspendedError as exc:raise HTTPException(403,str(exc))


async def owned(session,user,sid):
    item=await session.get(PracticeSession,sid)
    if item is None or item.user_id!=user.id:raise HTTPException(404,'Practice session not found')
    await require_content(session, user, item.problem_id, item.language)
    return item


def graph(session):
    return build_practice_graph(TransactionalSaver(session),default_deps())


def render(sid,state,balance=None):
    interrupt=pending_interrupt(state)
    return {'session_id':sid,'awaiting':interrupt.get('awaiting') if interrupt else None,
        'outcome':state.get('outcome',''),'reply':state.get('reply',''),
        'current_code':state.get('user_code',''),'recalled_moment':state.get('recalled_moment'),
        # Sessions stored before evidence was redacted are cleaned on the way out.
        'analysis':state.get('analysis'),'evidence':learner_safe(state.get('evidence'),state.get('problem_id','')),
        'tier_label':state.get('tier_label',''),'hint_tier':state.get('hint_tier',0),
        'step_back':state.get('step_back'),'attempts':state.get('attempts',0),
        'peppercorns_remaining':balance}


@router.post('/sessions')
async def start(request:StartRequest,user:User=Depends(get_current_user),session:AsyncSession=Depends(get_session),idempotency_key:str|None=Header(default=None)):
    active(user);validate_problem(request.problem_id,request.language)
    await require_content(session, user, request.problem_id, request.language)
    from app.services.learning_strikes import require_no_blocking
    await require_no_blocking(session, user.id, request.language, request.problem_id)
    async def work(_):
        await require_verified_reference(request.problem_id,request.language)
        item=PracticeSession(user_id=user.id,problem_id=request.problem_id,language=request.language,provider=request.provider)
        session.add(item);await session.flush()
        state=await graph(session).ainvoke({'user_id':user.id,'problem_id':item.problem_id,'language':item.language,'provider':item.provider},thread_config(user.id,item.problem_id,item.id),durability='sync')
        return render(item.id,state)
    return await perform(session,user.id,'practice:start',idempotency_key,request.model_dump(),0,'practice',work)


@router.get('/sessions/{sid}')
async def read(sid:str,user:User=Depends(get_current_user),session:AsyncSession=Depends(get_session)):
    active(user);item=await owned(session,user,sid)
    await recover_expired_scope(session,user.id,'practice:'+sid)
    state=await graph(session).aget_state(thread_config(user.id,item.problem_id,sid))
    result=render(sid,state.values)
    result['awaiting']=next((i.value.get('awaiting') for t in state.tasks for i in t.interrupts),None)
    result.update(problem_id=item.problem_id,language=item.language,provider=item.provider)
    return result


@router.post('/sessions/{sid}/actions')
async def action(sid:str,request:ActionRequest,user:User=Depends(get_current_user),session:AsyncSession=Depends(get_session),idempotency_key:str|None=Header(default=None)):
    active(user);item=await owned(session,user,sid)
    pid,lang,provider=item.problem_id,item.language,item.provider
    uid=user.id
    files=source_map=None
    if request.files is not None and request.action in ('submit','hint'):
        from app.services import workspace
        files=workspace.validate(lang,[f.model_dump() for f in request.files],request.entry or workspace.ENTRY.get(lang,''))
        bundled,source_map=workspace.bundle(lang,files,request.entry or workspace.ENTRY[lang])
        request=request.model_copy(update={'code':bundled})
    acquired=False
    finished=False
    import uuid
    from app.services.operations import operation_id
    idempotency_key = idempotency_key or str(uuid.uuid4())
    lock_token = operation_id(uid, 'practice:' + sid, idempotency_key)
    reserved_tier = 1
    profile_generation = None
    async def hint_price(_operation):
        nonlocal reserved_tier, profile_generation
        profile_generation = await session.scalar(select(User.profile_generation).where(User.id == uid))
        from app.services.hint_billing import reserve
        reserved_tier, price = await reserve(session, uid, pid, lang, _operation, request.max_hint_cost)
        return price
    cost=settings.analyze_cost if request.action=='submit' else hint_price if request.action=='hint' else 0
    reason='analyze' if request.action=='submit' else 'mentor' if request.action=='hint' else 'practice'
    async def prepare():
        nonlocal acquired
        # Serialize actions across workers. This flag commits with the receipt
        # and reservation; failures release it after rolling checkpoints back.
        locked=await session.execute(update(PracticeSession).where(PracticeSession.id==sid,PracticeSession.busy==False).values(busy=True,busy_token=lock_token))
        if not locked.rowcount:raise HTTPException(409,'Another action is processing for this session.')
        acquired=True
        snapshot=await graph(session).aget_state(thread_config(user.id,pid,sid))
        awaiting=next((i.value.get('awaiting') for t in snapshot.tasks for i in t.interrupts),None)
        if request.action=='reflect':
            if awaiting!='reflection' or not request.reasoning.strip():raise HTTPException(409,'Complete a successful evaluation before reflecting.')
        elif request.action!='quit' and awaiting!='learner':
            raise HTTPException(409,'This session is not awaiting that action.')
        if request.action=='submit':
            await require_verified_reference(pid,lang)
            if not request.code.strip():raise HTTPException(422,'Submit nonempty code.')
            await check_submission(session,user,request.code,lang)
        elif request.action=='hint':
            if not request.reasoning.strip():raise HTTPException(422,'Explain your reasoning before requesting a hint.')
            decision=await entitlements.check(session,user.id,lang)
            if not decision['entitled']:raise HTTPException(402,decision['reason'])
            try:await enforce_rate_limit(session,user.id,'hint')
            except RateLimitExceeded as exc:raise HTTPException(429,str(exc))
    async def work(balance):
        payload={'action':request.action,'code':request.code,'reasoning':request.reasoning}
        if request.action=='submit':
            payload['recalled_moment'] = await learning_profile.recall_similar_moment(session,user.id,_algorithms_for(pid),pid,lang)
        if request.action=='hint':
            payload.update(hint_tier=reserved_tier,
                recalled_moment=await learning_profile.recall_similar_moment(session,user.id,_algorithms_for(pid),pid,lang),
                profile_summary=(await learning_profile.build_profile(session,user.id)).summary())
        config=thread_config(user.id,pid,sid)
        if request.action=='quit':
            # End the stored graph even if it was waiting for reflection.
            current=await graph(session).aget_state(config)
            if any(i.value.get('awaiting')=='reflection' for t in current.tasks for i in t.interrupts):
                payload={'reasoning':''}
        state=await graph(session).ainvoke(Command(resume=payload),config,durability='sync')
        earned=[]
        if request.action=='submit':
            from app.services.content_access import can_reveal,solution_document
            from app.routers.workspace import add_checkpoint,case_report
            from app.db.models import WorkspaceRun
            evidence=state.get('evidence') or {}
            struck=[]
            completed=await save_evaluation(session,user.id,pid,lang,evidence,earned,struck)
            available=completed and bool(solution_document(pid,lang)) and await can_reveal(session,user.id,pid,lang)
            if earned:balance=earned[-1]['balance']
            from app.services.workspace import ENTRY
            entry=(request.entry or ENTRY[lang]) if files else ENTRY.get(lang,'solution.txt')
            snapshot=files or [{'name':entry,'content':request.code}]
            tests=case_report(evidence.get('curated'),lang,pid,source_map or [])
            session.add(WorkspaceRun(user_id=uid,problem_id=pid,language=lang,kind='evaluation',
                status=tests['status'],passed_cases=tests['passed'],total_cases=tests['total']))
            await add_checkpoint(session,uid,pid,lang,snapshot,entry,'evaluation',
                f"Evaluation: {tests['passed']}/{tests['total']} tests" if tests['total'] else 'Evaluation')
        else:available=False
        if request.action=='hint':
            await learning_profile.record_event(session,user.id,pid,kind='hint',language=lang,
                algorithms=_algorithms_for(pid),hint_tier=payload['hint_tier'],reasoning=request.reasoning,
                billing_operation_id=lock_token,expected_generation=profile_generation)
        if request.action=='reflect':
            await learning_profile.record_event(session,user.id,pid,kind='reflection',language=lang,algorithms=_algorithms_for(pid),reasoning=request.reasoning)
        await session.execute(update(PracticeSession).where(PracticeSession.id==sid,PracticeSession.busy_token==lock_token).values(busy=False,busy_token='',status='active' if pending_interrupt(state) else 'completed'))
        result=render(sid,state,balance);result['solution_available']=available;result['rewards']=earned
        if request.action=='submit':result['tests']=tests;result['source_map']=source_map;result['strike']=struck[0] if struck else None
        if request.action=='hint':
            from app.services.mentor import MAX_TIER,hint_cost
            from app.services.operations import current_balance
            result.update(peppercorns_charged=hint_cost(payload['hint_tier']),
                          next_hint_cost=hint_cost(min(payload['hint_tier']+1,MAX_TIER)))
            if balance is None:result['peppercorns_remaining']=await current_balance(session,uid)
        return result
    try:
        response = await perform(session,uid,'practice:'+sid,idempotency_key,request.model_dump(),cost,reason,work,prepare=prepare)
        finished=True
        return response
    finally:
        if acquired and not finished:
            await session.execute(update(PracticeSession).where(PracticeSession.id==sid,PracticeSession.busy_token==lock_token).values(busy=False,busy_token=""))
            await session.commit()


@router.get('/sessions/{sid}/summary')
async def summary(sid:str,user:User=Depends(get_current_user),session:AsyncSession=Depends(get_session)):
    """What happened in one practice session, from recorded events only."""
    from datetime import timezone
    from app.db.models import WorkspaceRun
    active(user);item=await owned(session,user,sid)
    started=item.created_at if item.created_at.tzinfo else item.created_at.replace(tzinfo=timezone.utc)
    scope=(LearningEvent.user_id==user.id,LearningEvent.problem_id==item.problem_id,
           LearningEvent.language==item.language,LearningEvent.created_at>=started)
    events=list((await session.scalars(select(LearningEvent).where(*scope).order_by(LearningEvent.created_at))).all())
    runs=list((await session.scalars(select(WorkspaceRun).where(WorkspaceRun.user_id==user.id,
        WorkspaceRun.problem_id==item.problem_id,WorkspaceRun.language==item.language,
        WorkspaceRun.created_at>=started).order_by(WorkspaceRun.created_at))).all())
    stamps=[e.created_at for e in events]+[r.created_at for r in runs]
    aware=[s if s.tzinfo else s.replace(tzinfo=timezone.utc) for s in stamps]
    evaluations=[r for r in runs if r.kind=='evaluation']
    categories=sorted({e.error_category for e in events if e.error_category})
    return {'session_id':sid,'problem_id':item.problem_id,'language':item.language,'status':item.status,
        'started_at':started.isoformat(),'last_activity':max(aware).isoformat() if aware else None,
        'elapsed_minutes':round((max(aware)-started).total_seconds()/60,1) if aware else 0,
        'test_runs':sum(r.kind=='run' for r in runs),
        'evaluations':[{'status':r.status,'passed':r.passed_cases,'total':r.total_cases,
                        'at':r.created_at.isoformat()} for r in evaluations],
        'solved':any(e.kind=='solved' for e in events),
        'hint_tiers':[e.hint_tier for e in events if e.kind=='hint'],
        'reflection':next((e.reasoning for e in reversed(events) if e.kind=='reflection'),None),
        'error_categories':categories}
