# Database models: users, the peppercorn transaction ledger, and chat history.
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    # Current balance is denormalized for fast reads; the Transaction table
    # is the source-of-truth ledger and every change writes both.
    peppercorns: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # "student" | "instructor" | "admin" — only instructor/admin may train the bot
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="student")
    # Chosen once, respected across every track and mode
    preferred_language: Mapped[str] = mapped_column(String(20), nullable=False, default="javascript")
    # "active" | "suspended" — suspended accounts cannot spend or submit
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    strikes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    suspended_reason: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user")
    threads: Mapped[list["ChatThread"]] = relationship(back_populates="user")


class Transaction(Base):
    """Append-only peppercorn ledger. Negative amount = debit, positive = credit."""

    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "chat", "analyze", "signup_bonus", "refund:chat"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="transactions")


class AdminAuditEvent(Base):
    __tablename__ = "admin_audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    actor_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    action: Mapped[str] = mapped_column(String(60), index=True)
    target_id: Mapped[str] = mapped_column(String(120), index=True)
    reason: Mapped[str] = mapped_column(String(500), default='')
    before_json: Mapped[str] = mapped_column(Text, default='{}')
    after_json: Mapped[str] = mapped_column(Text, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)


class InstructorLanguage(Base):
    __tablename__ = "instructor_languages"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    language: Mapped[str] = mapped_column(String(32), primary_key=True)
    assigned_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class ChatThread(Base):
    __tablename__ = "chat_threads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False, default="New conversation")
    language: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    subject: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    track: Mapped[str] = mapped_column(String(20), nullable=False, default="dsa")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="threads")
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="thread", order_by="ChatMessage.created_at"
    )


class ChatMessage(Base):
    """Persisted conversation memory — replaces the old in-process dict,
    so history survives restarts and works across multiple workers."""

    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    thread_id: Mapped[str] = mapped_column(ForeignKey("chat_threads.id"), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    thread: Mapped["ChatThread"] = relationship(back_populates="messages")


class Submission(Base):
    """A problem submitted through the training section, with its
    LLM-enrichment + execution-validation report."""

    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    problem_id: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    # "published" | "needs_review" | "failed"
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="needs_review")
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)      # what the instructor sent (JSON)
    report_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    markdown: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class SecurityEvent(Base):
    """Audit trail for every blocked submission. Retained even after a
    suspension so a human can review whether the action was warranted —
    an automated strike system without an appeal trail is not defensible."""

    __tablename__ = "security_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)   # block | warn
    reasons: Mapped[str] = mapped_column(Text, nullable=False)          # JSON list
    matched_rules: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    code_excerpt: Mapped[str] = mapped_column(Text, nullable=False, default="")
    context: Mapped[str] = mapped_column(String(40), nullable=False, default="analyze")
    counted_as_strike: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class Subscription(Base):
    """A per-language mentor subscription. Scoped to ONE programming language:
    a Python subscriber gets Socratic mentoring whenever they are coding in
    Python, across every track.

    Payment is handled entirely by Stripe Checkout — the card never reaches
    this server. `provider_ref` holds the Stripe subscription id so a webhook
    can extend or cancel it. Rows here are the entitlement record, not a
    payment record.
    """

    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    language: Mapped[str] = mapped_column(String(20), nullable=False)
    # "active" | "cancelled" | "expired"
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    provider_ref: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    provider_event_timestamp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class LearningEvent(Base):
    """One observable thing the learner did. Deliberately behavioural:
    what happened, on which problem, with which algorithm tags — never an
    inferred trait or personality judgement about the learner.
    """

    __tablename__ = "learning_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    problem_id: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    # "attempt" | "solved" | "hint" | "stepped_back" | "abandoned"
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    language: Mapped[str] = mapped_column(String(20), nullable=False, default="python")
    algorithms: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    # Deterministically derived from fuzz/test evidence, not from an LLM guess
    error_category: Mapped[str] = mapped_column(String(60), nullable=False, default="")
    detail: Mapped[str] = mapped_column(Text, nullable=False, default="")
    hint_tier: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # The learner's own words about their approach — the raw material for
    # reminding them how they reasoned through a similar situation before
    reasoning: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class TraceRecord(Base):
    """A finished trace, persisted for debugging and cost analysis.

    Stored as JSON rather than one row per span: traces are read whole (you
    want the entire tree for one request), never joined across, so a document
    shape fits the access pattern and keeps writes to a single insert.

    Retention is the operator's job — see `DELETE /admin/traces` and the
    note in the observability section of the README. Traces accumulate fast.
    """

    __tablename__ = "trace_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    trace_id: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False, default="")
    duration_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ok")
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    payload: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class KnowledgeDocument(Base):
    """A reference document uploaded through /learn.

    Uploaded text reaches every learner's prompt, so it is gated: an admin's
    upload publishes immediately, an instructor's waits as "pending" until an
    admin approves it. The extracted text is kept so an admin can review
    exactly what will be indexed, and so approval can index it later.

    `chunk_ids` holds the vector-store ids written for this document (JSON
    list). Deleting by id works identically on Chroma and pgvector, unlike
    metadata filters.
    """

    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False, default=".txt")
    track: Mapped[str] = mapped_column(String(20), nullable=False, default="custom")
    language: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    # "pending" | "published" | "rejected"
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default="pending")
    text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    characters: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    chunk_ids: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    review_note: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    reviewed_by: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


class ServiceOperation(Base):
    """Durable request receipt; debit and terminal response share transactions."""
    __tablename__ = "service_operations"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    scope: Mapped[str] = mapped_column(String(100))
    fingerprint: Mapped[str] = mapped_column(String(64))
    state: Mapped[str] = mapped_column(String(20), default="running")
    amount: Mapped[int] = mapped_column(Integer, default=0)
    reason: Mapped[str] = mapped_column(String(100), default="")
    http_status: Mapped[int] = mapped_column(Integer, default=200)
    response_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class PracticeSession(Base):
    __tablename__ = "practice_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    problem_id: Mapped[str] = mapped_column(String(120))
    language: Mapped[str] = mapped_column(String(20))
    provider: Mapped[str] = mapped_column(String(20))
    busy: Mapped[bool] = mapped_column(Boolean, default=False)
    busy_token: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class PracticeCheckpoint(Base):
    __tablename__ = "practice_checkpoints"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    thread_id: Mapped[str] = mapped_column(String(255), index=True)
    namespace: Mapped[str] = mapped_column(String(255), default="")
    checkpoint_id: Mapped[str] = mapped_column(String(64))
    parent_id: Mapped[str] = mapped_column(String(64), default="")
    checkpoint_data: Mapped[str] = mapped_column(Text)
    metadata_data: Mapped[str] = mapped_column(Text)
    writes_json: Mapped[str] = mapped_column(Text, default="{}")


class WebhookReceipt(Base):
    __tablename__ = "webhook_receipts"
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    payload_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class VectorCleanupJob(Base):
    """Transactional outbox: retain failed vector deletion until it succeeds."""
    __tablename__ = "vector_cleanup_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    chunk_ids: Mapped[str] = mapped_column(Text, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
