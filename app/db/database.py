# Async SQLAlchemy setup. SQLite locally; the same code works against
# Postgres by changing DATABASE_URL (e.g. postgresql+asyncpg://...).
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)

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

    if "users" not in tables:
        raise RuntimeError(
            "Database schema is not initialised. Run:  alembic upgrade head"
        )
