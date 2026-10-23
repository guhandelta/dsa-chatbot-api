# /study — the Study Room: path-aware coaching modes, quizzes and next steps.
#
# Messages (explain, debug, compare) come out of a daily free pool and then
# cost `study_message_cost` each; pricing is decided under the per-user lock
# by `perform`. Quizzes, the path, notes and "what next" are free.
from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import ChatMessage, ChatThread, User
from app.services import learning_path, quiz, study_room
from app.services.language_access import allowed_languages, require_language
from app.services.strikes import AccountSuspendedError, assert_active

router = APIRouter(prefix="/study", tags=["study"])


class StudyMessage(BaseModel):
    language: str = Field(min_length=1, max_length=32)
    mode: Literal["explain", "debug", "compare"] = "explain"
    message: str = Field(min_length=1, max_length=4000)
    thread_id: str | None = Field(default=None, max_length=36)
    focus_id: str | None = Field(default=None, min_length=1, max_length=120)
    compare_language: str | None = Field(default=None, max_length=32)
    code: str = Field(default="", max_length=20000)
    error: str = Field(default="", max_length=4000)
    provider: Literal["openai", "claude", "gemini", "auto"] = "auto"


class DebugResolution(BaseModel):
    thread_id: str = Field(min_length=1, max_length=36)
    fix: str = Field(min_length=1, max_length=4000)


class QuizStart(BaseModel):
    language: str = Field(min_length=1, max_length=32)
    node_id: str | None = Field(default=None, max_length=120)
    count: int = Field(default=4, ge=1, le=8)


class QuizReply(BaseModel):
    item_id: str = Field(min_length=1, max_length=200)
    response: str | int = Field(...)


def active(user: User) -> None:
    try:
        assert_active(user)
    except AccountSuspendedError as exc:
        raise HTTPException(403, str(exc))


@router.get("/readiness")
async def readiness(user: User = Depends(get_current_user)):
    """Which languages the existing content can support, and how."""
    return {"languages": [learning_path.readiness(lang) for lang in learning_path.LANGUAGE_LABELS],
            "levels": learning_path.LEVEL_LABELS}


@router.get("/path")
async def path(language: str, user: User = Depends(get_current_user),
               session: AsyncSession = Depends(get_session)):
    await require_language(session, user, language)
    state = await learning_path.progress(session, user.id, language)
    return {**state, "label": learning_path.LANGUAGE_LABELS.get(language, language),
            "readiness": learning_path.readiness(language), "levels": learning_path.LEVEL_LABELS}


@router.get("/explain-pathway")
async def explain_pathway(language: str, user: User = Depends(get_current_user),
                          session: AsyncSession = Depends(get_session)):
    await require_language(session, user, language)
    from app.services.explain_pathway import pathway
    return await pathway(session, user.id, language)


@router.get("/nodes/{node_id}/lesson")
async def lesson(node_id: str, language: str, user: User = Depends(get_current_user),
                 session: AsyncSession = Depends(get_session)):
    await require_language(session, user, language)
    node = learning_path.find_node(language, node_id)
    if node is None:
        raise HTTPException(404, "That path node does not exist for this language.")
    return {"node": node, "markdown": study_room.lesson_markdown(language, node)}


@router.get("/allowance")
async def allowance(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await study_room.allowance(session, user.id)


@router.get("/progress-overview")
async def progress_overview(language: str, user: User = Depends(get_current_user),
                            session: AsyncSession = Depends(get_session)):
    await require_language(session, user, language)
    from app.services.study_progress import overview
    return await overview(session, user.id, language)


@router.get("/next")
async def what_next(language: str, user: User = Depends(get_current_user),
                    session: AsyncSession = Depends(get_session)):
    await require_language(session, user, language)
    return await study_room.recommend(session, user.id, language)


@router.get("/notes")
async def notes(language: str, user: User = Depends(get_current_user),
                session: AsyncSession = Depends(get_session)):
    await require_language(session, user, language)
    permitted = await allowed_languages(session, user)
    rows = await study_room.notes(session, user.id, language)
    return {"notes": [n for n in rows if n["mode"] != "compare" or
                      all(n["body"].get(key) in permitted for key in ("first", "second"))]}


@router.get("/evidence")
async def evidence(language: str, user: User = Depends(get_current_user),
                   session: AsyncSession = Depends(get_session)):
    """Concepts the learner has shown in their own passing code."""
    await require_language(session, user, language)
    return {"language": language, "items": await quiz.evidence(session, user.id, language)}


@router.get("/insights")
async def insights(language: str, user: User = Depends(get_current_user),
                   session: AsyncSession = Depends(get_session)):
    await require_language(session, user, language)
    return await quiz.insights(session, user.id, language)


async def _thread(session: AsyncSession, user: User, request: StudyMessage) -> ChatThread | None:
    if not request.thread_id:
        return None
    thread = await session.get(ChatThread, request.thread_id)
    if thread is None or thread.user_id != user.id:
        raise HTTPException(404, "Thread not found")
    if (thread.language, thread.track) != (request.language, "study-" + request.mode):
        raise HTTPException(409, "Start a new conversation when changing language or mode.")
    if not thread.study_focus_id:
        raise HTTPException(409, "This older conversation has no saved focus. Start a new conversation.")
    if thread.study_focus_id and request.focus_id and thread.study_focus_id != request.focus_id:
        raise HTTPException(409, "Start a new conversation when changing focus.")
    if thread.compare_language and thread.compare_language != request.compare_language:
        raise HTTPException(409, "Start a new conversation when changing comparison language.")
    return thread


@router.post("/message")
async def message(request: StudyMessage, user: User = Depends(get_current_user),
                  session: AsyncSession = Depends(get_session),
                  idempotency_key: str | None = Header(default=None)):
    from app.services.chat_model_routing import configured_providers, run_routed_chat
    from app.services.llm_router import get_llm
    from app.services.operations import current_balance, perform
    from app.services.rag_pipeline import build_history
    from app.services.rate_limit import RateLimitExceeded, enforce_rate_limit
    active(user)
    await require_language(session, user, request.language)
    if request.mode == "compare":
        if not request.compare_language or request.compare_language == request.language:
            raise HTTPException(422, "Choose a second language to compare with.")
        await require_language(session, user, request.compare_language)
        if {request.language, request.compare_language} != {"javascript", "typescript"}:
            raise HTTPException(422, "Comparisons are available only for JavaScript and TypeScript.")
    if request.mode == "debug" and not (request.code.strip() and request.error.strip()):
        raise HTTPException(422, "Paste your code and the actual error or output.")
    provider = "auto" if user.role == "student" else request.provider
    existing_thread = await _thread(session, user, request)
    focus_id = (existing_thread.study_focus_id if existing_thread else None) or request.focus_id
    focus = await study_room.resolve_focus(session, user.id, request.language, focus_id)

    async def prepare():
        if provider == "auto" and not configured_providers():
            raise HTTPException(503, "The tutor is temporarily unavailable. Please try again later.")
        try:
            await enforce_rate_limit(session, user.id, "study")
        except RateLimitExceeded as exc:
            raise HTTPException(429, str(exc))

    async def price(_operation):
        return await study_room.message_price(session, user.id)

    async def work(balance):
        thread = await _thread(session, user, request)
        rows = []
        if thread:
            rows = list((await session.scalars(select(ChatMessage).where(ChatMessage.thread_id == thread.id)
                                               .order_by(ChatMessage.created_at.desc()).limit(20))).all())
            rows.reverse()
        history = build_history(rows)
        await session.commit()
        extra: dict = {}
        if request.mode == "explain":
            system = study_room.explain_prompt(request.language, focus,
                                               study_room.focus_context(request.language, focus, request.message))
            user_text = request.message
        elif request.mode == "debug":
            tier = study_room.debug_tier(sum(1 for r in rows if r.role == "assistant"))
            from app.services.mentor import TIERS
            extra.update(hint_tier=tier, tier_label=TIERS[tier][0])
            system = study_room.debug_prompt(request.language, focus, tier)
            user_text = study_room.debug_message(request.message, request.code, request.error)
        else:
            contexts = study_room.compare_context(request.language, request.compare_language, request.message, focus)
            system = study_room.compare_prompt(request.language, request.compare_language, focus, contexts)
            user_text = request.message

        async def generate(selected):
            return await study_room.generate(get_llm(selected), system, history, user_text)

        answer, routing = await run_routed_chat(request.message, history, provider, generate)
        node_id = focus["id"] if focus["kind"] == "node" else None
        note = None
        if request.mode == "explain":
            answer, card = study_room.split_takeaway(answer)
            if card:
                note = await study_room.save_note(session, user.id, request.language, node_id, "explain",
                                                  card["concept"], card)
                extra["takeaway"] = card
        elif request.mode == "debug":
            answer = study_room.guard_socratic(answer, extra["hint_tier"], request.error)
        else:
            note = await study_room.save_note(session, user.id, request.language, node_id, "compare",
                                              f"{request.language} vs {request.compare_language}: {request.message[:120]}",
                                              {"first": request.language, "second": request.compare_language,
                                               "question": request.message, "comparison": answer})
        if thread is None:
            thread = ChatThread(user_id=user.id, title=request.message[:120], language=request.language,
                                track="study-" + request.mode)
            session.add(thread)
            await session.flush()
        thread.study_focus_id = focus["id"] or ""
        thread.compare_language = request.compare_language or ""
        stored = request.message if request.mode != "debug" else user_text
        session.add_all([ChatMessage(thread_id=thread.id, role="user", content=stored),
                         ChatMessage(thread_id=thread.id, role="assistant", content=answer)])
        charged = 0 if balance is None else settings.study_message_cost
        return {"answer": answer, "thread_id": thread.id, "mode": request.mode,
                "focus": {k: focus[k] for k in ("kind", "id", "title", "auto")},
                "note_id": note.id if note else None, "peppercorns_charged": charged,
                "peppercorns_remaining": balance if balance is not None else await current_balance(session, user.id),
                "model_routing": routing, **extra}

    result = await perform(session, user.id, "study", idempotency_key,
                           {**request.model_dump(), "provider": provider}, price, "study", work, prepare=prepare)
    return {**result, "allowance": await study_room.allowance(session, user.id)}


@router.post("/debug/resolve")
async def resolve_debug(request: DebugResolution, user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_session)):
    """The learner fixed it: log their misconception and their own fix. Free."""
    active(user)
    thread = await session.get(ChatThread, request.thread_id)
    if thread is None or thread.user_id != user.id or thread.track != "study-debug":
        raise HTTPException(404, "Debug conversation not found")
    await require_language(session, user, thread.language)
    first = await session.scalar(select(ChatMessage.content).where(
        ChatMessage.thread_id == thread.id, ChatMessage.role == "user").order_by(ChatMessage.created_at).limit(1))
    note = await study_room.save_note(session, user.id, thread.language, thread.study_focus_id or None, "debug", "Misconception logged",
                                      {"thread_id": thread.id, "what_i_thought": first or "", "my_fix": request.fix})
    await session.commit()
    return study_room.note_view(note)


@router.post("/quiz")
async def start_quiz(request: QuizStart, user: User = Depends(get_current_user),
                     session: AsyncSession = Depends(get_session)):
    active(user)
    await require_language(session, user, request.language)
    started = await quiz.start(session, user, request.language, request.node_id, request.count)
    await session.commit()
    return started


@router.post("/quiz/{quiz_id}/answer")
async def answer_quiz(quiz_id: str, request: QuizReply, user: User = Depends(get_current_user),
                      session: AsyncSession = Depends(get_session)):
    active(user)
    row = await quiz.owned(session, user, quiz_id)
    await require_language(session, user, row.language)
    provider = quiz.judge_provider()
    return await quiz.answer(session, user, quiz_id, request.item_id, request.response, provider)


@router.get("/quiz/{quiz_id}")
async def quiz_summary(quiz_id: str, user: User = Depends(get_current_user),
                       session: AsyncSession = Depends(get_session)):
    row = await quiz.owned(session, user, quiz_id)
    if row.language not in await allowed_languages(session, user):
        raise HTTPException(403, "An active subscription covering this language is required.")
    return await quiz.summary(session, user, quiz_id)


class DebugChallengeSelection(BaseModel):
    language: str = Field(min_length=1, max_length=32)
    subject: str = Field(min_length=1, max_length=80)
    difficulty: Literal['easy', 'medium', 'hard', 'expert', 'extreme'] = 'easy'
    focus_id: str | None = Field(default=None, min_length=1, max_length=120)


class DebugChallengeReview(BaseModel):
    diagnosis: str = Field(min_length=10, max_length=4000)


async def _debug_topic(session, user, language, focus_id):
    if focus_id:
        return focus_id
    # Older clients also stay on the current topic; omission must not widen
    # the pool to every framework/problem in the language.
    from app.services.learning_path import LANGUAGE_LABELS
    if language not in LANGUAGE_LABELS:
        return 'subject:' + language
    current = await study_room.resolve_focus(session, user.id, language, None)
    if not current['id']:
        raise HTTPException(409, 'Choose a path topic to continue debugging.')
    return current['id']


@router.get('/debug/challenges')
async def debug_catalog(language: str, focus_id: str | None = None, user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_session)):
    await require_language(session, user, language)
    from app.services import debug_challenges
    focus_id = await _debug_topic(session, user, language, focus_id)
    return await debug_challenges.catalog(session, user, language, focus_id)


@router.post('/debug/challenges/next')
async def next_debug_challenge(request: DebugChallengeSelection, user: User = Depends(get_current_user),
                               session: AsyncSession = Depends(get_session)):
    await require_language(session, user, request.language)
    from app.services import debug_challenges
    focus_id = await _debug_topic(session, user, request.language, request.focus_id)
    return await debug_challenges.next_challenge(session, user, request.language, request.subject, request.difficulty, focus_id)


@router.post('/debug/challenges/{attempt_id}/review')
async def review_debug_challenge(attempt_id: str, request: DebugChallengeReview,
                                 user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    from app.services import debug_challenges
    return await debug_challenges.review(session, user, attempt_id, request.diagnosis.strip())
