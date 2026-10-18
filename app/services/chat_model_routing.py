"""Bounded tutor model selection. Routing rules are policy, not quality rankings.

The graph routes only generation; authorization, retrieval scope, and billing
remain in the chat endpoint. No extra LLM call is spent classifying a question.
"""
import asyncio
import logging
import re
from collections.abc import Awaitable, Callable
from typing import Any, TypedDict

import httpx
from fastapi import HTTPException
from langgraph.graph import END, START, StateGraph

from app.core.config import settings

logger = logging.getLogger(__name__)
PROVIDERS = ('gemini', 'openai', 'claude')


def configured_providers() -> list[str]:
    credentials = {'gemini': settings.google_api_key,
                   'openai': settings.openai_api_key,
                   'claude': settings.anthropic_api_key}
    return [p for p in PROVIDERS if credentials[p].strip() and model_name(p).strip()]


def model_name(provider: str) -> str:
    return {'gemini': settings.gemini_model, 'openai': settings.openai_model,
            'claude': settings.anthropic_model}[provider]


def classify_question(message: str, history: list) -> str:
    def classify(text):
        if re.search(r'```|\b(debug|traceback|exception|refactor|stack trace|review (?:my|this|the) code)\b', text, re.I):
            return 'code'
        if re.search(r'\b(complexity|prove|proof|optimal|optimi[sz]e|trade.?offs?|compare|recurrence)\b', text, re.I):
            return 'reasoning'
        return 'explain'

    task = classify(message)
    # Short follow-ups inherit the most recent user question's task. System
    # prompts and retrieved text never get to change routing preferences.
    if task == 'explain' and len(message) < 160 and re.search(r'\b(why|that|this|it|again|continue)\b', message, re.I):
        for item in reversed(history[-4:]):
            if getattr(item, 'type', None) == 'human':
                return classify(str(item.content))
    return task


def candidates_for(task: str) -> list[str]:
    preferred = {'explain': settings.chat_explain_provider,
                 'code': settings.chat_code_provider,
                 'reasoning': settings.chat_reasoning_provider}[task]
    available = configured_providers()
    ordered = dict.fromkeys((preferred, settings.default_provider, *PROVIDERS))
    # At most two generation attempts, independent of how many keys exist.
    return [p for p in ordered if p in available][:2]


def can_fallback(error: Exception) -> bool:
    if isinstance(error, HTTPException):
        return False  # Never bypass an application rejection.
    if isinstance(error, (TimeoutError, ConnectionError, httpx.TimeoutException, httpx.NetworkError)):
        return True
    status = getattr(error, 'status_code', None) or getattr(error, 'status', None)
    if not isinstance(status, int):
        status = getattr(error, 'code', None)
    if isinstance(status, int):
        return status in (401, 403, 404, 408, 429) or 500 <= status <= 599
    kind = getattr(error, 'kind', type(error).__name__)
    return kind in ('APIConnectionError', 'APITimeoutError', 'ServiceUnavailable', 'ResourceExhausted', 'DeadlineExceeded')


class RoutingState(TypedDict, total=False):
    task: str
    candidates: list[str]
    result: Any
    routing: dict


async def run_routed_chat(message: str, history: list, provider: str,
                          generate: Callable[[str], Awaitable[Any]]) -> tuple[Any, dict]:
    if provider != 'auto':
        result = await generate(provider)
        return result, {'strategy': 'manual', 'task': None, 'provider': provider,
                        'model': model_name(provider), 'fallback_used': False}

    def classify(state):
        return {'task': classify_question(message, history)}

    def select(state):
        candidates = candidates_for(state['task'])
        if not candidates:
            raise HTTPException(503, 'The tutor is temporarily unavailable. Please try again later.')
        return {'candidates': candidates}

    async def answer(state):
        for index, selected in enumerate(state['candidates']):
            try:
                async with asyncio.timeout(settings.chat_model_timeout_seconds):
                    result = await generate(selected)
                logger.info('Tutor routing: task=%s provider=%s model=%s fallback=%s',
                            state['task'], selected, model_name(selected), index > 0)
                return {'result': result, 'routing': {
                    'strategy': 'automatic', 'task': state['task'],
                    'provider': selected, 'model': model_name(selected),
                    'fallback_used': index > 0}}
            except Exception as error:
                if not can_fallback(error):
                    raise
                logger.warning('Tutor provider unavailable: provider=%s error_type=%s',
                               selected, type(error).__name__)
        raise RuntimeError('Automatic tutor providers could not complete this request.') from None

    graph = StateGraph(RoutingState)
    graph.add_node('classify', classify)
    graph.add_node('select', select)
    graph.add_node('answer', answer)
    graph.add_edge(START, 'classify')
    graph.add_edge('classify', 'select')
    graph.add_edge('select', 'answer')
    graph.add_edge('answer', END)
    outcome = await graph.compile().ainvoke({})
    return outcome['result'], outcome['routing']
