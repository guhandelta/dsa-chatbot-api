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
from app.services.operations import perform,recover_expired_scope
from app.services.practice_checkpoints import TransactionalSaver
from app.services.strikes import assert_active,AccountSuspendedError
from app.services.rate_limit import enforce_rate_limit,RateLimitExceeded

router=APIRouter(prefix='/practice',tags=['practice'])

class StartRequest(BaseModel):
    problem_id:str=Field(min_length=1,max_length=120)
    language:str
    provider:Provider='gemini'

class ActionRequest(BaseModel):
    action:Literal['submit','hint','reflect','quit']
    code:str=Field(default='',max_length=20000)
    reasoning:str=Field(default='',max_length=4000)


def active(user):
    try:assert_active(user)
    except AccountSuspendedError as exc:raise HTTPException(403,str(exc))


async def owned(session,user,sid):
    item=await session.get(PracticeSession,sid)
    if item is None or item.user_id!=user.id:raise HTTPException(404,'Practice session not found')
    return item


def graph(session):
    return build_practice_graph(TransactionalSaver(session),default_deps())


def render(sid,state,balance=None):
    interrupt=pending_interrupt(state)
    return {'session_id':sid,'awaiting':interrupt.get('awaiting') if interrupt else None,
        'outcome':state.get('outcome',''),'reply':state.get('reply',''),
        'current_code':state.get('user_code',''),'recalled_moment':state.get('recalled_moment'),
        'analysis':state.get('analysis'),'evidence':state.get('evidence'),
        'tier_label':state.get('tier_label',''),'hint_tier':state.get('hint_tier',0),
        'step_back':state.get('step_back'),'attempts':state.get('attempts',0),
        'peppercorns_remaining':balance}


@router.post('/sessions')
async def start(request:StartRequest,user:User=Depends(get_current_user),session:AsyncSession=Depends(get_session),idempotency_key:str|None=Header(default=None)):
    active(user);validate_problem(request.problem_id,request.language)
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
    acquired=False
    finished=False
    import uuid
    from app.services.operations import operation_id
    idempotency_key = idempotency_key or str(uuid.uuid4())
    lock_token = operation_id(uid, 'practice:' + sid, idempotency_key)
    cost=settings.analyze_cost if request.action=='submit' else settings.mentor_cost if request.action=='hint' else 0
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
            payload.update(hint_tier=await _current_tier(session,user.id,pid,lang),
                recalled_moment=await learning_profile.recall_similar_moment(session,user.id,_algorithms_for(pid),pid,lang),
                profile_summary=(await learning_profile.build_profile(session,user.id)).summary())
        config=thread_config(user.id,pid,sid)
        if request.action=='quit':
            # End the stored graph even if it was waiting for reflection.
            current=await graph(session).aget_state(config)
            if any(i.value.get('awaiting')=='reflection' for t in current.tasks for i in t.interrupts):
                payload={'reasoning':''}
        state=await graph(session).ainvoke(Command(resume=payload),config,durability='sync')
        if request.action=='submit':
            available=await save_evaluation(session,user.id,pid,lang,state.get('evidence') or {})
        else:available=False
        if request.action=='hint':
            await learning_profile.record_event(session,user.id,pid,kind='hint',language=lang,algorithms=_algorithms_for(pid),hint_tier=payload['hint_tier'],reasoning=request.reasoning)
        if request.action=='reflect':
            await learning_profile.record_event(session,user.id,pid,kind='reflection',language=lang,algorithms=_algorithms_for(pid),reasoning=request.reasoning)
        await session.execute(update(PracticeSession).where(PracticeSession.id==sid,PracticeSession.busy_token==lock_token).values(busy=False,busy_token='',status='active' if pending_interrupt(state) else 'completed'))
        result=render(sid,state,balance);result['solution_available']=available
        return result
    try:
        response = await perform(session,uid,'practice:'+sid,idempotency_key,request.model_dump(),cost,reason,work,prepare=prepare)
        finished=True
        return response
    finally:
        if acquired and not finished:
            await session.execute(update(PracticeSession).where(PracticeSession.id==sid,PracticeSession.busy_token==lock_token).values(busy=False,busy_token=""))
            await session.commit()
