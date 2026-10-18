import sys
import asyncio
from contextlib import suppress
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure project root is in sys.path when executed directly as a script
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import init_db
from app.routers import (
    admin,
    admin_dashboard,
    analyze,
    auth,
    chat,
    learn,
    mentor,
    problems,
    practice,
    subscriptions,
    tracks,
    training,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic migrations once you deploy)
    await init_db()
    from app.services.maintenance import worker
    task = asyncio.create_task(worker(), name="knowledge-and-operation-maintenance")
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


app = FastAPI(title="DSA RAG Chatbot API", version="2.0.0", lifespan=lifespan)

# Allowed origins come from .env (CORS_ORIGINS), not hardcoded
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(learn.router)
app.include_router(chat.router)
app.include_router(analyze.router)
app.include_router(problems.router)
app.include_router(practice.router)
app.include_router(tracks.router)
app.include_router(mentor.router)
app.include_router(subscriptions.router)
app.include_router(training.router)
app.include_router(admin.router)
app.include_router(admin_dashboard.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
