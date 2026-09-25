# Abstracts Claude, Gemini, and OpenAI behind a single interface.
# Returns a LangChain-compatible chat model based on the provider name.
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.core.config import settings


def get_llm(provider: str):
    """Factory function — returns the right LangChain chat model.

    Model IDs come from settings so they can be bumped via .env.
    All calls go through `ainvoke`, so no `streaming` flag is needed here;
    if/when SSE streaming is added, use `astream` on the same objects.
    """
    if provider == "openai":
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.3,
        )
    elif provider == "claude":
        return ChatAnthropic(
            model=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
            temperature=0.3,
            max_tokens=2048,
        )
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0.3,
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
