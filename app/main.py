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
    courses,
    learn,
    mentor,
    problems,
    practice,
    study,
    subscriptions,
    tracks,
    training,
    workspace,
    strikes,
    playground,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_execution_policy()
    if settings.exec_backend == "docker":
        # Validate image pinning and CLI availability before accepting requests.
        from app.services.container_executor import command
        command(["true"], _root, "dsa-startup-validation")
    settings.validate_production_policy()
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
app.include_router(learn.router, prefix="/teach")
# Existing clients keep working; new documentation and the UI use /teach.
app.include_router(learn.router, prefix="/learn", include_in_schema=False)
app.include_router(courses.router)
app.include_router(chat.router)
app.include_router(analyze.router)
app.include_router(problems.router)
app.include_router(practice.router)
app.include_router(workspace.router)
app.include_router(strikes.router)
app.include_router(playground.router)
app.include_router(tracks.router)
app.include_router(mentor.router)
app.include_router(study.router)
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
