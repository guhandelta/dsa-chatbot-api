# Centralized settings loaded from .env using pydantic-settings
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # API keys for each LLM provider
    openai_api_key: str
    anthropic_api_key: str = ""
    google_api_key: str = ""

    # Default LLM provider (can be overridden per request)
    default_provider: str = "openai"

    # Model IDs (override via .env without touching code)
    openai_model: str = "gpt-4o-mini"
    anthropic_model: str = "claude-sonnet-4-20250514"
    gemini_model: str = "gemini-2.0-flash"

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

    # Database — SQLite for local dev, swap for Postgres in production
    database_url: str = "sqlite+aiosqlite:///./dsa_chatbot.db"

    # Auth
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # CORS — comma-separated origins
    cors_origins: str = "http://localhost:3000"

    # Emails auto-promoted to admin on register/login (comma-separated)
    admin_emails: str = ""

    # Sandbox limits for executing submitted solutions
    exec_timeout_seconds: int = 8
    exec_memory_mb: int = 512
    # Max processes the sandboxed child may create (blocks fork bombs)
    exec_max_processes: int = 16
    # Max bytes of stdout captured from a run
    exec_max_output_bytes: int = 65536

    # Three-strike policy for malicious submissions
    max_strikes: int = 3
    # Submissions per user per hour (execution is expensive)
    submissions_per_hour: int = 30

    # Peppercorn economy
    signup_bonus: int = 50
    chat_cost: int = 1
    analyze_cost: int = 5
    mentor_cost: int = 2

    # Stripe — checkout is hosted by Stripe; no card data reaches this server
    stripe_webhook_secret: str = ""

    # Tests and throwaway databases only. Real environments run migrations.
    auto_create_tables: bool = False

    # Observability. Tracing is cheap (in-memory spans, one insert per
    # request) but can be disabled entirely if needed.
    tracing_enabled: bool = True
    # Traces older than this are removed by DELETE /admin/traces?older_than_days=
    trace_retention_days: int = 14

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def admin_email_list(self) -> list[str]:
        return [e.strip().lower() for e in self.admin_emails.split(",") if e.strip()]


settings = Settings()
