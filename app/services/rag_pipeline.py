# Core RAG pipeline: retrieve relevant DSA context, then generate a response.
#
# Rewritten without the deprecated ConversationalRetrievalChain /
# ConversationBufferWindowMemory. Conversation history now comes from the
# database (passed in by the router), so it survives restarts and works
# across multiple workers. All LLM calls are async (`ainvoke`) so they
# don't block the FastAPI event loop.
import asyncio

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from app.services.knowledge_base import get_vectorstore
from app.services.llm_router import get_llm

# Keep the last N exchanges (user+assistant pairs) in the prompt window
HISTORY_WINDOW_MESSAGES = 20  # = 10 exchanges


def build_history(rows: list) -> list[BaseMessage]:
    """Converts persisted ChatMessage rows into LangChain message objects,
    keeping only the most recent window."""
    recent = rows[-HISTORY_WINDOW_MESSAGES:]
    out: list[BaseMessage] = []
    for row in recent:
        if row.role == "user":
            out.append(HumanMessage(content=row.content))
        else:
            out.append(AIMessage(content=row.content))
    return out


def _coerce_text(content) -> str:
    """LLM content can be a string or a list of content blocks (Anthropic)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "".join(parts)
    return str(content)


TRACK_PERSONA = {
    "language": (
        "You are teaching {language} itself: syntax, built-in data structures, "
        "idioms, and the standard library. Keep examples in {language} only. "
        "Explain WHY an idiom exists, not just how to type it."
    ),
    "dsa": (
        "You are a DSA interview coach working through LeetCode/HackerRank style "
        "problems. The user codes in {language}. Prefer hints and guiding questions "
        "before revealing a full solution."
    ),
    "algorithm": (
        "You are teaching algorithms as concepts: the invariant, why it is correct, "
        "its complexity, and the signals in a problem statement that indicate this "
        "technique. Show code in {language} only after the idea is clear, and always "
        "name the family of problems the technique unlocks."
    ),
}


async def run_rag_chat(
    message: str,
    provider: str,
    history: list[BaseMessage],
    language: str,
    track: str = "dsa",
    focus_id: str | None = None,
) -> str:
    """
    1. Retrieves the top-4 relevant DSA problem chunks from ChromaDB.
    2. Injects them + conversation history into the LLM prompt.
    3. Returns the LLM's answer as a string.
    """
    llm = get_llm(provider)
    vectorstore = get_vectorstore()

    # Scope retrieval to the active track so a Python-syntax question doesn't
    # surface graph theory. Teacher uploads tagged "custom" (POST /learn/train)
    # are shared reference material and ride along with every track. A
    # focus_id narrows further to one specific item.
    track_filter: dict = {"track": {"$in": [track, "custom"]}}
    where: dict = track_filter
    if focus_id:
        where = {"$and": [track_filter, {"problem_id": focus_id}]}

    def _search():
        try:
            return vectorstore.similarity_search(message, k=4, filter=where)
        except Exception:
            # Older collections may lack the track field — fall back rather
            # than failing the user's message.
            return vectorstore.similarity_search(message, k=4)

    docs = await asyncio.to_thread(_search)
    if not docs and focus_id:
        docs = await asyncio.to_thread(
            lambda: vectorstore.similarity_search(message, k=4, filter=track_filter)
        )
    context = "\n\n---\n\n".join(doc.page_content for doc in docs)
    if not context:
        context = "(No matching documents found in the knowledge base.)"

    persona = TRACK_PERSONA.get(track, TRACK_PERSONA["dsa"]).format(language=language)
    system_prompt = f"""{persona}

Use the retrieved context below when relevant; if it isn't, answer from your
own knowledge and say so. Walk through examples step by step.

Retrieved context:
{context}"""

    messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]
    messages.extend(history)
    messages.append(HumanMessage(content=message))

    response = await llm.ainvoke(messages)
    return _coerce_text(response.content)
