# Async SQLAlchemy setup. SQLite locally; the same code works against
# Postgres by changing DATABASE_URL (e.g. postgresql+asyncpg://...).
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(settings.resolved_database_url, echo=False)

SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields a DB session per request."""
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Verify the schema is migrated. Tables are owned by Alembic, not by
    create_all — otherwise the app silently creates a schema that diverges
    from the migration history, and the first real deployment breaks.

    Run `alembic upgrade head` before starting. Set AUTO_CREATE_TABLES=true
    only for throwaway test databases.
    """
    from sqlalchemy import inspect

    from app.core.config import settings
    from app.db import models  # noqa: F401  — registers the tables

    if settings.auto_create_tables:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return

    async with engine.begin() as conn:
        tables = await conn.run_sync(lambda sync: inspect(sync).get_table_names())
        practice_columns = await conn.run_sync(lambda sync: {c["name"] for c in inspect(sync).get_columns("practice_sessions")}) if "practice_sessions" in tables else set()

        knowledge_columns = await conn.run_sync(lambda sync: {c["name"] for c in inspect(sync).get_columns("knowledge_documents")}) if "knowledge_documents" in tables else set()

        thread_columns = await conn.run_sync(lambda sync: {c["name"] for c in inspect(sync).get_columns("chat_threads")}) if "chat_threads" in tables else set()

    if not {"users", "service_operations", "practice_sessions", "practice_checkpoints", "webhook_receipts", "vector_cleanup_jobs", "instructor_languages", "admin_audit_events", "debug_challenge_attempts", "workspace_drafts", "workspace_checkpoints", "workspace_runs", "learning_strikes", "challenge_sets", "challenge_answers"}.issubset(tables) or "busy_token" not in practice_columns or "language" not in knowledge_columns or not {"language", "subject", "track"}.issubset(thread_columns):
        raise RuntimeError(
            "Database schema is not initialised. Run:  alembic upgrade head"
        )
