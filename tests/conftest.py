# Shared fixtures: a fresh in-memory SQLite database per test and an
# httpx client bound to the FastAPI app with the DB dependency overridden.
# No network or API keys required — the LLM layer is mocked in the tests
# that touch it.
import os

import pytest
import pytest_asyncio

# Provide dummy settings BEFORE importing the app, so config validation passes
os.environ.setdefault("EXEC_BACKEND", "subprocess")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("JWT_SECRET", "test-secret-for-offline-tests-at-least-32-bytes")
os.environ.setdefault("SIGNUP_BONUS", "50")
os.environ.setdefault("AUTO_CREATE_TABLES", "true")
os.environ.setdefault("CHAT_COST", "1")
os.environ.setdefault("ANALYZE_COST", "5")

from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.db.database import Base, get_session  # noqa: E402
from app.main import app  # noqa: E402


@pytest_asyncio.fixture
async def session_factory():
    # StaticPool keeps the single in-memory DB alive across connections
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest_asyncio.fixture
async def db(session_factory):
    async with session_factory() as s:
        yield s


@pytest_asyncio.fixture
async def client(session_factory):
    async def override_get_session():
        async with session_factory() as s:
            yield s

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def isolate_training_history(tmp_path, monkeypatch):
    # Importer tests must never append temporary runs to the application's log.
    from app.services import training_registry
    monkeypatch.setattr(training_registry, 'LOG_FILE', tmp_path / 'training-events.json')


@pytest.fixture
def subscribe_user(db):
    async def subscribe(user_id, *languages):
        from app.services.entitlements import grant
        for language in languages:
            await grant(db, user_id, language, days=42)
        await db.commit()
    return subscribe


@pytest.fixture(autouse=True)
def isolate_curated_semantic_provider(monkeypatch):
    # Local maintenance may have published a real index. Unit tests must never
    # send fixture questions to its provider; dedicated tests can override this.
    monkeypatch.setattr('app.services.reference_semantics.search', lambda *a, **kw: [])
