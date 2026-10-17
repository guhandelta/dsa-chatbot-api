# /chat endpoints — auth-gated RAG conversations with persisted history.
#
# Flow per message:
#   1. Verify the thread belongs to the user (or create one).
#   2. Atomically debit the chat cost — committed BEFORE the LLM call so a
#      concurrent request can't double-spend.
#   3. Run the RAG pipeline. If the provider errors, refund the debit.
#   4. Persist both messages and return the answer + remaining balance.
import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import ChatMessage, ChatThread, User
from app.models.schemas import ChatRequest, ChatResponse, MessageOut, ThreadOut
from app.services.peppercorns import InsufficientPeppercornsError, credit, debit
from app.services.rag_pipeline import build_history, run_rag_chat

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


async def _get_or_create_thread(
    session: AsyncSession, user: User, thread_id: str | None, first_message: str
) -> ChatThread:
    if thread_id:
        thread = await session.get(ChatThread, thread_id)
        if thread is None or thread.user_id != user.id:
            raise HTTPException(status_code=404, detail="Thread not found")
        return thread

    thread = ChatThread(user_id=user.id, title=first_message[:120])
    session.add(thread)
    await session.flush()
    return thread


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: User = Depends(get_current_user),
               session: AsyncSession = Depends(get_session),
               idempotency_key: str | None = Header(default=None)):
    from app.services.operations import perform
    from app.services.strikes import assert_active, AccountSuspendedError
    from app.services.rate_limit import enforce_rate_limit, RateLimitExceeded
    try:
        assert_active(current_user)
    except AccountSuspendedError as exc:
        raise HTTPException(403, str(exc))
    async def prepare():
        if request.retrieval_mode == 'agentic':
            from app.services.agentic_rag import MAX_MESSAGE_BYTES
            if not settings.agentic_rag_enabled or current_user.role != 'admin':
                raise HTTPException(403, 'The private agentic retrieval experiment is unavailable.')
            if len(request.message.encode()) > MAX_MESSAGE_BYTES:
                raise HTTPException(422, 'Experimental questions must fit within 6000 UTF-8 bytes.')
        if request.thread_id:
            await _get_or_create_thread(session, current_user, request.thread_id, request.message)
        if request.subject:
            from app.services.reference_library import subjects
            selected = next((s for s in subjects() if s['id'] == request.subject), None)
            if selected is None:
                raise HTTPException(422, 'Unknown reference subject.')
            if selected['language'] != request.language or request.track != 'language' or request.focus_id:
                raise HTTPException(422, 'Choose the subject language and Language track without a lesson focus.')
        try:
            await enforce_rate_limit(session, current_user.id, 'chat')
        except RateLimitExceeded as exc:
            raise HTTPException(429, str(exc))
    async def work(balance):
        # Read history without acquiring SQLite's writer lock during generation.
        if request.thread_id:
            thread = await _get_or_create_thread(session, current_user, request.thread_id, request.message)
            rows = list((await session.scalars(select(ChatMessage).where(ChatMessage.thread_id==thread.id).order_by(ChatMessage.created_at.desc()).limit(20))).all())
            rows.reverse()
        else:
            thread, rows = None, []
        history=build_history(rows)
        await session.commit()
        citations=[]
        retrieval=None
        if request.retrieval_mode == 'agentic':
            from app.services.agentic_rag import ReadOnlyTools, Scope, run
            result=await run(request.message,request.provider,history,ReadOnlyTools(session,
                Scope(request.language or current_user.preferred_language,request.track,request.focus_id,request.subject)))
            answer,citations,retrieval=result.answer,result.sources,result.report
        else:
            from app.services.uploaded_knowledge import search as search_uploads
            uploads = await search_uploads(session, request.message, request.track,
                request.language or current_user.preferred_language, request.focus_id, request.subject)
            upload_options = {"uploaded_documents": uploads, "citations": citations} if uploads else {}
            answer = await run_rag_chat(message=request.message, provider=request.provider,
                history=history, language=request.language or current_user.preferred_language,
                track=request.track, focus_id=request.focus_id,
                **({"subject":request.subject} if request.subject else {}), **upload_options)
        if thread is None:
            thread=await _get_or_create_thread(session,current_user,None,request.message)
        session.add_all([ChatMessage(thread_id=thread.id, role='user', content=request.message),
                         ChatMessage(thread_id=thread.id, role='assistant', content=answer)])
        return ChatResponse(answer=answer, thread_id=thread.id, peppercorns_remaining=balance, sources=citations, retrieval=retrieval)
    return await perform(session,current_user.id,'chat',idempotency_key,request.model_dump(),
                         settings.chat_cost,'chat',work,prepare=prepare)


@router.get("/threads", response_model=list[ThreadOut])
async def list_threads(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(ChatThread)
        .where(ChatThread.user_id == current_user.id)
        .order_by(ChatThread.created_at.desc())
    )
    return [ThreadOut.model_validate(t) for t in result.scalars()]


@router.get("/threads/{thread_id}/messages", response_model=list[MessageOut])
async def thread_messages(
    thread_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    thread = await session.get(ChatThread, thread_id)
    if thread is None or thread.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Thread not found")
    result = await session.execute(
        select(ChatMessage)
        .where(ChatMessage.thread_id == thread_id)
        .order_by(ChatMessage.created_at)
    )
    return [MessageOut.model_validate(m) for m in result.scalars()]


@router.get("/capabilities")
async def capabilities(user: User = Depends(get_current_user)):
    return {"agentic_retrieval": settings.agentic_rag_enabled and user.role == 'admin'}
