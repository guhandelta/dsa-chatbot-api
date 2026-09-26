"""Alembic environment.

Reads DATABASE_URL from app settings rather than alembic.ini, so migrations
always target the same database the app uses. Async URLs are converted to
their sync driver for migration runs — Alembic drives DDL synchronously.
"""
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402
from app.db.database import Base  # noqa: E402
from app.db import models  # noqa: F401,E402  — registers every table

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _sync_url() -> str:
    """Alembic runs DDL synchronously; translate the async driver."""
    url = settings.database_url
    return (
        url.replace("+aiosqlite", "")
        .replace("+asyncpg", "+psycopg2")
        .replace("+aiomysql", "+pymysql")
    )


def run_migrations_offline() -> None:
    context.configure(
        url=_sync_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,      # SQLite needs batch mode to ALTER
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section) or {}
    section["sqlalchemy.url"] = _sync_url()
    connectable = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,   # SQLite cannot ALTER COLUMN without it
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
