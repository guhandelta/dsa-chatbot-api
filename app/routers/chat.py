# /chat endpoints — auth-gated RAG conversations with persisted history.
#
# Flow per message:
#   1. Verify the thread belongs to the user (or create one).
#   2. Atomically debit the chat cost — committed BEFORE the LLM call so a
#      concurrent request can't double-spend.
#   3. Run the RAG pipeline. If the provider errors, refund the debit.
#   4. Persist both messages and return the answer + remaining balance.
import logging

from fastapi import APIRouter, Depends, HTTPException
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
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    thread = await _get_or_create_thread(session, current_user, request.thread_id, request.message)

    # --- Debit first (atomic), so the spend is reserved before we pay for tokens
    try:
        balance = await debit(session, current_user.id, settings.chat_cost, reason="chat")
    except InsufficientPeppercornsError as exc:
        raise HTTPException(status_code=402, detail=str(exc))
    await session.commit()

    # --- Load persisted history for this thread
    result = await session.execute(
        select(ChatMessage)
        .where(ChatMessage.thread_id == thread.id)
        .order_by(ChatMessage.created_at)
    )
    history = build_history(list(result.scalars()))

    # --- Call the LLM; refund on provider failure
    try:
        answer = await run_rag_chat(
            message=request.message,
            provider=request.provider,
            history=history,
            # fall back to the learner's saved language preference
            language=request.language or current_user.preferred_language,
            track=request.track,
            focus_id=request.focus_id,
        )
    except Exception:
        logger.exception("RAG chat failed; refunding %s peppercorns", settings.chat_cost)
        balance = await credit(session, current_user.id, settings.chat_cost, reason="refund:chat")
        await session.commit()
        raise HTTPException(
            status_code=502,
            detail="The AI provider failed to respond. Your peppercorns were refunded.",
        )

    # --- Persist the exchange
    session.add_all(
        [
            ChatMessage(thread_id=thread.id, role="user", content=request.message),
            ChatMessage(thread_id=thread.id, role="assistant", content=answer),
        ]
    )
    await session.commit()

    return ChatResponse(answer=answer, thread_id=thread.id, peppercorns_remaining=balance)


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
