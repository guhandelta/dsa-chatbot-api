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
    # "student" | "teacher" | "admin" — only teacher/admin may train the bot
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="student")
    # Chosen once, respected across every track and mode
    preferred_language: Mapped[str] = mapped_column(String(20), nullable=False, default="python")
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


class ChatThread(Base):
    __tablename__ = "chat_threads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False, default="New conversation")
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
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)      # what the teacher sent (JSON)
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
