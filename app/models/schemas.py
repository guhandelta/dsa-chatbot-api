# Pydantic models for request/response validation
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional

Provider = Literal["openai", "claude", "gemini"]


# ---------- Auth ----------

class RegisterRequest(BaseModel):
    email: EmailStr
    # bcrypt only hashes the first 72 bytes, so cap input there
    password: str = Field(min_length=8, max_length=72)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=72)


class UserOut(BaseModel):
    id: str
    email: EmailStr
    peppercorns: int
    role: str = "student"
    preferred_language: str = "python"
    status: str = "active"
    strikes: int = 0

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Learn (knowledge-base uploads) ----------

KnowledgeStatus = Literal["pending", "published", "rejected"]


class LearnTrainResponse(BaseModel):
    status: str = "success"
    document_id: str
    # "published" when indexed now, "pending" when awaiting admin review
    review_status: KnowledgeStatus
    filename: str
    file_type: str
    characters_extracted: int
    chunks_trained: int
    track: str = "custom"
    message: str
    retrieval_status: str = "awaiting_approval"
    reference_language: str | None = None
    reference_chunks: int = 0


class KnowledgeDocumentOut(BaseModel):
    id: str
    owner_id: str
    owner_email: str = ""
    filename: str
    file_type: str
    track: str
    status: KnowledgeStatus
    characters: int
    chunks: int
    review_note: str = ""
    created_at: datetime | None = None
    reviewed_at: datetime | None = None


    retrieval_status: str = "awaiting_approval"
    reference_language: str | None = None
    reference_chunks: int = 0
    projection_version: str = ""


class KnowledgeDocumentDetail(KnowledgeDocumentOut):
    # First part of the extracted text, so a reviewer can see what would be
    # injected into learners' prompts before approving it.
    preview: str


class KnowledgeReviewRequest(BaseModel):
    note: str = Field(default="", max_length=500)


# ---------- Chat ----------

Track = Literal["language", "dsa", "algorithm"]


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    thread_id: Optional[str] = None          # For conversation memory
    provider: Provider = "gemini"
    language: str = Field(default="python", min_length=1, max_length=32) # e.g. "python", "java", "cpp"
    mode: Literal["learn", "practice"] = "learn"
    retrieval_mode: Literal["standard", "agentic"] = "standard"
    # Which of the three learning tracks this conversation belongs to.
    # Scopes retrieval so a Python-basics question doesn't pull graph theory.
    track: Track = "dsa"
    # Optional focus: a specific content item or algorithm tag
    focus_id: Optional[str] = Field(default=None, min_length=1, max_length=120)
    subject: str | None = Field(default=None, min_length=1, max_length=80, pattern=r"^[a-z0-9-]+$")


class SourceCitation(BaseModel):
    document_id: str
    filename: str
    revision: str
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    thread_id: str
    peppercorns_remaining: int
    sources: list[SourceCitation] = Field(default_factory=list)
    retrieval: dict | None = None


class ThreadOut(BaseModel):
    id: str
    title: str

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    role: str
    content: str

    model_config = {"from_attributes": True}


# ---------- Analyze ----------

class AnalyzeRequest(BaseModel):
    problem_id: str = Field(min_length=1, max_length=120)  # e.g. "two-sum"
    user_code: str = Field(min_length=1, max_length=20000)
    language: str
    provider: Provider = "openai"


class AnalysisResult(BaseModel):
    """Structured feedback. Also used directly as the LLM's output schema
    via `llm.with_structured_output(AnalysisResult)` — the field descriptions
    below are part of the prompt."""

    mistakes: list[str] = Field(description="Bugs or logic errors in the user's code")
    enhancements: list[str] = Field(
        description="Better approaches and time/space complexity improvements"
    )
    watchouts: list[str] = Field(
        description="Edge cases the user missed, e.g. empty input, overflow"
    )
    interview_tips: list[str] = Field(
        description="Follow-up questions an interviewer typically asks about this problem"
    )
    overall_feedback: str = Field(description="A 2-3 sentence high-level summary")


class AnalyzeResponse(BaseModel):
    solution_available: bool = False
    analysis: AnalysisResult
    peppercorns_remaining: int
    # Real execution results when the problem has verified test cases.
    # None means feedback is review-only and must not claim verification.
    execution: Optional[dict] = None
    # Full verification evidence: curated cases, fuzzing, complexity.
    # The UI shows this so feedback is auditable rather than taken on faith.
    evidence: Optional[dict] = None


# ---------- Training (instructor/admin) ----------

Role = Literal["student", "instructor", "admin"]


class RoleUpdate(BaseModel):
    role: Role


class TrainRequest(BaseModel):
    # slug used as the filename and vector-store key
    problem_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,80}$")
    # The problem statement, or just a name/description — the LLM expands it
    problem: str = Field(min_length=5, max_length=20000)
    # Optional partial solutions keyed by language; missing ones get generated
    solutions: dict[str, str] = Field(default_factory=dict)
    provider: Provider = "openai"


class SubmissionOut(BaseModel):
    id: str
    problem_id: str
    status: str
    created_at: str


class LanguagePreference(BaseModel):
    language: Literal["python", "javascript", "java", "cpp", "c", "rust"]


# ---------- Mentor & subscriptions ----------

class MentorRequest(BaseModel):
    problem_id: str = Field(min_length=1, max_length=120)
    language: str = "python"
    # The learner must say what they are thinking before a hint is given.
    # This is the pedagogy, not a formality: the mentor responds to THEIR
    # reasoning, not to the problem in the abstract.
    reasoning: str = Field(min_length=1, max_length=4000)
    current_code: str = Field(default="", max_length=20000)
    provider: Provider = "openai"


class MentorResponse(BaseModel):
    reply: str
    hint_tier: int
    tier_label: str
    recalled_moment: Optional[str] = None      # their own earlier reasoning
    step_back_offer: Optional[dict] = None     # an easier problem or the concept
    peppercorns_remaining: int


class SubscriptionOut(BaseModel):
    id: str
    language: str
    status: str
    expires_at: str

    model_config = {"from_attributes": True}


class EntitlementOut(BaseModel):
    language: str
    entitled: bool
    reason: str
    expires_at: Optional[str] = None
