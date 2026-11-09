# Database models: users, the peppercorn transaction ledger, and chat history.
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, Index
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
    profile_generation: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
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


class HintUsage(Base):
    """Minimal billing history, independent of erasable learning-profile text.

    A reservation commits with the service debit; failed operations do not
    consume a tier. Legacy events are linked by ID to avoid double counting.
    """
    __tablename__ = "hint_usage"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    problem_id: Mapped[str] = mapped_column(String(120), nullable=False)
    language: Mapped[str] = mapped_column(String(32), nullable=False)
    tier: Mapped[int] = mapped_column(Integer, nullable=False)
    operation_id: Mapped[str | None] = mapped_column(ForeignKey("service_operations.id"), unique=True)
    event_id: Mapped[str | None] = mapped_column(String(36), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class RewardGrant(Base):
    """One earn-back reward, at most once per key (e.g. a first independent
    solve, a completed stage, a streak day). The unique key is what makes a
    retried request or a recomputed progress view unable to pay twice."""

    __tablename__ = "reward_grants"
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_reward_grants_user_key"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    key: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class QuizSession(Base):
    """One Study Room quiz: the items drawn for a path node and the running score.
    Answers live server-side only; the client never receives an answer key."""

    __tablename__ = "quiz_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    language: Mapped[str] = mapped_column(String(32), nullable=False)
    node_id: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    items_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    answered: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Sum of per-item scores; free-text answers can earn partial credit.
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class QuizAnswer(Base):
    """The learner's own answer to one quiz item, kept so typed responses can
    show how they understand a concept and where the weak spots are."""

    __tablename__ = "quiz_answers"
    __table_args__ = (UniqueConstraint("quiz_id", "item_id", name="uq_quiz_answers_quiz_item"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    quiz_id: Mapped[str] = mapped_column(ForeignKey("quiz_sessions.id"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    item_id: Mapped[str] = mapped_column(String(200), nullable=False)
    item_type: Mapped[str] = mapped_column(String(20), nullable=False)
    concept: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    response: Mapped[str] = mapped_column(Text, nullable=False, default="")
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    feedback: Mapped[str] = mapped_column(Text, nullable=False, default="")
    grading: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    misconception: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    understanding_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)


class UnderstandingCheckEvent(Base):
    """Usage reservations, including retries and failed model calls; no answer text."""
    __tablename__ = 'understanding_check_events'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, index=True)


class StudyNote(Base):
    """Something a Study Room session produced for the learner to keep: a
    takeaway card, a logged misconception, or a side-by-side comparison."""

    __tablename__ = "study_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    language: Mapped[str] = mapped_column(String(32), nullable=False)
    node_id: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    # "explain" | "debug" | "compare"
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)


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
    study_focus_id: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    compare_language: Mapped[str] = mapped_column(String(32), nullable=False, default="")
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


class SectionEntitlement(Base):
    """Future section rights, independent of the current language subscription."""

    __tablename__ = "section_entitlements"
    __table_args__ = (Index("ix_section_entitlements_owner_section", "user_id", "section"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    section: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="manual")
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)


class LearningEvent(Base):
    """One observable thing the learner did. Deliberately behavioural:
    what happened, on which problem, with which algorithm tags — never an
    inferred trait or personality judgement about the learner.
    """

    __tablename__ = "learning_events"
    __table_args__ = (Index("ix_learning_events_user_created", "user_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    # Nullable for historical events and non-practice learning activity.
    # New practice events carry the graph session that produced them.
    practice_session_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
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


class StudentPathRecord(Base):
    """Student-authored goals and reasoning; never assessment evidence by itself."""

    __tablename__ = "student_path_records"
    __table_args__ = (Index("ix_student_path_records_owner_scope_time", "user_id", "section", "language", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    section: Mapped[str] = mapped_column(String(32), nullable=False)
    language: Mapped[str] = mapped_column(String(32), nullable=False)
    kind: Mapped[str] = mapped_column(String(20), nullable=False)
    concept_id: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    body: Mapped[str] = mapped_column(Text, nullable=False)
    curriculum_version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)


class TraceRecord(Base):
    """A finished trace, persisted for debugging and cost analysis.

    Stored as JSON rather than one row per span: traces are read whole (you
    want the entire tree for one request), never joined across, so a document
    shape fits the access pattern and keeps writes to a single insert.

    Retention is the operator's job — see `DELETE /admin/traces` and the
    note in the observability section of the README. Traces accumulate fast.
    """

    __tablename__ = "trace_records"
    __table_args__ = (Index("ix_trace_records_created", "created_at"),)

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


class DebugChallengeAttempt(Base):
    """A problem is reserved once per learner, even across devices or retries."""
    __tablename__ = "debug_challenge_attempts"
    __table_args__ = (UniqueConstraint("user_id", "challenge_id", name="uq_debug_challenge_user_problem"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    challenge_id: Mapped[str] = mapped_column(String(80), nullable=False)
    language: Mapped[str] = mapped_column(String(32), nullable=False)
    subject: Mapped[str] = mapped_column(String(80), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="assigned")
    diagnosis: Mapped[str] = mapped_column(Text, nullable=False, default="")
    understanding_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class WorkspaceDraft(Base):
    """The learner's autosaved practice files for one problem in one language.
    `revision` increases on every save so a stale tab cannot silently
    overwrite newer work."""

    __tablename__ = "workspace_drafts"
    __table_args__ = (UniqueConstraint("user_id", "problem_id", "language", name="uq_workspace_draft"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    problem_id: Mapped[str] = mapped_column(String(120), nullable=False)
    language: Mapped[str] = mapped_column(String(20), nullable=False)
    template: Mapped[str] = mapped_column(String(40), nullable=False, default="single")
    entry: Mapped[str] = mapped_column(String(64), nullable=False)
    files_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class WorkspaceCheckpoint(Base):
    """A named snapshot of the workspace files the learner can restore."""

    __tablename__ = "workspace_checkpoints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    problem_id: Mapped[str] = mapped_column(String(120), nullable=False)
    language: Mapped[str] = mapped_column(String(20), nullable=False)
    # "manual" | "evaluation" | "before_reset" | "before_restore"
    kind: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    label: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    entry: Mapped[str] = mapped_column(String(64), nullable=False)
    files_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)


class WorkspaceRun(Base):
    """One execution of the learner's workspace against the problem's tests:
    a free practice run, or the test stage of a paid evaluation."""

    __tablename__ = "workspace_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    # Free workspace runs may be outside a graph session; evaluations created
    # by /practice are bound to the session that produced them.
    practice_session_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    problem_id: Mapped[str] = mapped_column(String(120), nullable=False)
    language: Mapped[str] = mapped_column(String(20), nullable=False)
    # "run" | "evaluation"
    kind: Mapped[str] = mapped_column(String(20), nullable=False, default="run")
    # "pending" | "passed" | "failed" | "unverified" | "error"
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    passed_cases: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_cases: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)


class ChallengeSet(Base):
    """Questions a learner answers to clear a learning strike, or extra
    practice they asked for. Items are quiz-bank ids; answers stay server-side."""

    __tablename__ = "challenge_sets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    language: Mapped[str] = mapped_column(String(32), nullable=False)
    # Path node the questions come from, and the problem that led here.
    node_id: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    problem_id: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    # "strike" | "extra"
    kind: Mapped[str] = mapped_column(String(20), nullable=False)
    items_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    required: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    answered: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ChallengeAnswer(Base):
    __tablename__ = "challenge_answers"
    __table_args__ = (UniqueConstraint("set_id", "item_id", name="uq_challenge_answer_item"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    set_id: Mapped[str] = mapped_column(ForeignKey("challenge_sets.id"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    item_id: Mapped[str] = mapped_column(String(200), nullable=False)
    item_type: Mapped[str] = mapped_column(String(20), nullable=False)
    concept: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    response: Mapped[str] = mapped_column(Text, nullable=False, default="")
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)


class LearningStrike(Base):
    """A mistake in a paid evaluation or a strike-clearing question. Not the
    abuse strikes in `strikes`: these are a learning device, cleared by
    answering related questions. They snowball up to a configured cap."""

    __tablename__ = "learning_strikes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    language: Mapped[str] = mapped_column(String(32), nullable=False)
    problem_id: Mapped[str] = mapped_column(String(120), nullable=False)
    node_id: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    # "evaluation" | "challenge"
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    # Where the mistake happened: phase, failure category, tests passed, file/line, concept.
    where_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    set_id: Mapped[str | None] = mapped_column(ForeignKey("challenge_sets.id"), nullable=True)
    # "open" | "cleared"
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    cleared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
