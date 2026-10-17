"""LangGraph orchestration for multi-step, interactive flows.

LangGraph owns control flow (what happens next, when to pause for the
learner). LangChain still does the work inside each node: retrieval through
the vector store and model calls through app.services.llm_router.get_llm.
"""
