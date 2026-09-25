# FastAPI application entry point. Registers routers, CORS, and DB setup.
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import init_db
from app.routers import (
    admin,
    analyze,
    auth,
    chat,
    mentor,
    problems,
    subscriptions,
    tracks,
    training,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic migrations once you deploy)
    await init_db()
    yield


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
app.include_router(chat.router)
app.include_router(analyze.router)
app.include_router(problems.router)
app.include_router(tracks.router)
app.include_router(mentor.router)
app.include_router(subscriptions.router)
app.include_router(training.router)
app.include_router(admin.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
