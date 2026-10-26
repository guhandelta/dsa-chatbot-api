# Centralized settings loaded from .env using pydantic-settings
from pathlib import Path
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(ENV_PATH if ENV_PATH.exists() else ".env"), extra="ignore")

    # API keys for each LLM provider
    openai_api_key: str
    anthropic_api_key: str = ""
    google_api_key: str = ""

    # Default LLM provider (can be overridden per request)
    default_provider: str = "openai"

    # Tutor routing preferences; tune with representative questions and costs.
    chat_explain_provider: Literal['gemini', 'openai', 'claude'] = 'gemini'
    chat_code_provider: Literal['gemini', 'openai', 'claude'] = 'claude'
    chat_reasoning_provider: Literal['gemini', 'openai', 'claude'] = 'openai'
    chat_model_timeout_seconds: float = Field(default=45, ge=1, le=120)

    # Model IDs (override via .env without touching code)
    openai_model: str = "gpt-4o-mini"
    anthropic_model: str = "claude-sonnet-4-20250514"
    gemini_model: str = "gemini-3.8-flash"

    # Vector store backend: "chroma" (embedded, zero setup) or "pgvector"
    # (Postgres/Supabase — one database for everything, scales horizontally).
    vector_store: str = "chroma"

    # ChromaDB persistence directory (used only when vector_store == "chroma")
    chroma_persist_dir: str = "./chroma_db"

    # Vectors reuse DATABASE_URL by default. Set this only if they live in a
    # different database from the app's relational data.
    vector_database_url: str = ""

    # Changing this invalidates every stored vector — re-ingest after any change.
    embedding_model: str = "text-embedding-3-small"
    embedding_provider: str = ""  # "google", "openai", or "" (auto-detect)

    # Database — SQLite for local dev, swap for Postgres in production
    database_url: str = "sqlite+aiosqlite:///./dsa_chatbot.db"

    # Auth
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # CORS — comma-separated origins
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"

    # Emails auto-promoted to admin on register/login (comma-separated)
    admin_emails: str = ""

    # Sandbox limits for executing submitted solutions
    app_env: Literal["development", "test", "production"] = "development"
    exec_backend: Literal["subprocess", "docker"] = "docker"
    exec_container_image: str = ""
    exec_timeout_seconds: int = 8
    exec_memory_mb: int = 512
    # Per-container process limit (host subprocess mode cannot enforce this)
    exec_max_processes: int = 64
    # Max bytes of stdout captured from a run
    exec_max_output_bytes: int = 65536

    # Three-strike policy for malicious submissions
    max_strikes: int = 3
    # Submissions per user per hour (execution is expensive)
    submissions_per_hour: int = 30
    # Mentor turns per hour (separate budget — hints are cheaper than reviews)
    hints_per_hour: int = 60
    chats_per_hour: int = 60
    # Fixed hint-cycle length (six weeks); anchored per learner/problem/language
    hint_tier_reset_hours: int = Field(default=1008, ge=1)

    # Optional JDK location; JAVA_HOME is read from .env by Settings.
    java_home: str = ""

    # Peppercorn economy
    signup_bonus: int = 50
    chat_cost: int = 1
    analyze_cost: int = 5
    mentor_cost: int = 2
    # Mentor hint tiers up to and including this one are free on every
    # problem (Orient, Probe the gap); higher tiers cost `mentor_cost`.
    free_hint_tiers: int = Field(default=2, ge=0, le=4)
    # Study Room: a daily free pool of messages, then `study_message_cost`.
    study_daily_free_messages: int = Field(default=5, ge=0)
    study_message_cost: int = Field(default=1, ge=0)
    # Earn-back rewards for independent work.
    reward_independent_solve: int = Field(default=3, ge=0)
    reward_streak: int = Field(default=5, ge=0)
    reward_streak_days: int = Field(default=7, ge=2)
    reward_stage_complete: int = Field(default=10, ge=0)
    # Quiz answers are free; these hourly caps bound grading and execution cost.
    # Sized so one sitting can finish the largest path (see tests/test_learning_path_walkthrough.py).
    quiz_answers_per_hour: int = 300
    quiz_code_runs_per_hour: int = 100
    # Practice workspace: free test runs (no review, no LLM) and stored snapshots.
    workspace_runs_per_hour: int = Field(default=120, ge=0)
    workspace_max_checkpoints: int = Field(default=30, ge=1)
    # When a reference solution may be revealed. Product decision (2026-10-26):
    # solutions stay hidden; learners clear strikes instead. The other values
    # remain for courses that choose differently.
    #   after_evaluation - after `solution_reveal_min_evaluations` completed evaluations
    #   after_pass       - only after a passing evaluation
    #   disabled         - never reveal reference solutions
    solution_reveal_policy: Literal["after_evaluation", "after_pass", "disabled"] = "disabled"
    solution_reveal_min_evaluations: int = Field(default=1, ge=1)
    # Learning strikes: a failed paid evaluation earns one; a wrong answer to a
    # clearing question earns another ("snowball"), up to the cap.
    learning_strike_cap: int = Field(default=4, ge=1)
    # What happens when a wrong answer would pass the cap. UNDECIDED PRODUCT
    # RULE, so it is a hook: "mentor_step_back" offers an easier prerequisite
    # and a mentor hint; "lock" stops new questions until a mentor session.
    learning_strike_cap_action: Literal["mentor_step_back", "lock"] = "mentor_step_back"
    # Open strikes in a language block starting a different problem in it.
    learning_strikes_gate_progress: bool = True
    # Extra practice the learner asks for: sets per calendar month (UTC),
    # not yet split by section.
    extra_practice_sets_per_month: int = Field(default=40, ge=0)

    # Stripe — checkout is hosted by Stripe; no card data reaches this server
    stripe_webhook_secret: str = ""

    # Tests and throwaway databases only. Real environments run migrations.
    auto_create_tables: bool = False

    # Private opt-in agentic retrieval pilot; ordinary RAG remains the default.
    agentic_rag_enabled: bool = False

    # Observability. Tracing is cheap (in-memory spans, one insert per
    # request) but can be disabled entirely if needed.
    tracing_enabled: bool = True
    # Traces older than this are removed by DELETE /admin/traces?older_than_days=
    trace_retention_days: int = 14


    def validate_execution_policy(self) -> None:
        if self.app_env == "production" and self.exec_backend != "docker":
            raise RuntimeError("Production requires EXEC_BACKEND=docker")

    def production_problems(self) -> list[str]:
        """Settings that are unsafe in production, whatever APP_ENV currently says.

        Startup refuses to run when APP_ENV=production and this is non-empty;
        tools/doctor.py reports the same list as warnings before then.
        """
        problems = []
        if self.exec_backend != "docker":
            problems.append("EXEC_BACKEND must be docker")
        if self.jwt_secret in ("", "dev-secret-change-me") or "change-me" in self.jwt_secret or len(self.jwt_secret) < 32:
            problems.append("JWT_SECRET is missing, a placeholder, or shorter than 32 characters")
        origins = self.cors_origin_list
        local = ("localhost", "127.0.0.1", "[::1]", "0.0.0.0")
        if not origins or all(o.split("://", 1)[-1].split(":")[0].split("/")[0] in local for o in origins):
            problems.append("CORS_ORIGINS lists only local origins; set the deployed UI origin")
        if "*" in origins:
            problems.append("CORS_ORIGINS must not contain *")
        if self.auto_create_tables:
            problems.append("AUTO_CREATE_TABLES must be false; run alembic upgrade head")
        placeholders = [e for e in self.admin_email_list
                        if e.endswith(("@example.com", "@example.org", "@example.net")) or e in ("admin", "you")]
        if placeholders:
            problems.append("ADMIN_EMAILS contains placeholder address(es): " + ", ".join(placeholders)
                            + " (anyone who registers one becomes admin)")
        if self.database_url.startswith("sqlite"):
            problems.append("DATABASE_URL is SQLite; use Postgres for multi-worker production")
        return problems

    def validate_production_policy(self) -> None:
        if self.app_env == "production":
            problems = self.production_problems()
            if problems:
                raise RuntimeError("Unsafe production configuration:\n  - " + "\n  - ".join(problems))

    @property
    def resolved_database_url(self) -> str:
        if self.database_url.startswith("sqlite+aiosqlite:///./"):
            rel = self.database_url.replace("sqlite+aiosqlite:///./", "")
            return f"sqlite+aiosqlite:///{ENV_PATH.parent / rel}"
        return self.database_url

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def admin_email_list(self) -> list[str]:
        return [e.strip().lower() for e in self.admin_emails.split(",") if e.strip()]


settings = Settings()
