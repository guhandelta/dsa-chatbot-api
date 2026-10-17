"""Practice session as a LangGraph state machine.

    START -> load_context -> await_learner <--------------------------+
                               |  submit / hint / quit                 |
                 +-------------+-------------+                         |
               submit         hint          quit -> END                |
                 |              |                                      |
              screen        mentor_hint --(tier < MAX)---------------->+
           blocked | ok         |                                      |
                 |   |       (tier = MAX) -> step_back --------------->+
                 |  evaluate                                           |
                 |   | passed      -> await_reflection -> END          |
                 |   | failed      -> diagnose ----------------------->+
                 |   | unverified ------------------------------------>+
                 +-------------------------------------------------- ->+

DESIGN RULES (these mirror the guarantees of /analyze and /mentor):

* Routing is deterministic. Edges branch on execution evidence and hint tier,
  never on an LLM's opinion. Models only produce text inside nodes.
* No billing or DB writes in here. LangGraph re-runs an interrupted node from
  its first line on resume, so a debit inside a node could charge twice. The
  router does assert_active / rate limit / debit / refund / record_event
  around each resume, exactly as the existing routers do.
* Each interrupt() lives in its own node with nothing before it, so a resume
  never repeats side effects.
* Hint tier is NOT counted here. The router computes it from LearningEvent
  rows (with the reset window in routers/mentor._current_tier) and passes it
  in the resume payload, so there is a single source of truth.
* "Passed" requires evidence that something actually ran. A language the
  harness cannot execute yet (e.g. Go) yields "unverified", not "passed".

Every external capability is injected through PracticeDeps, so the real app
uses the real LLM/sandbox/vector store while tests can substitute fakes.
"""
import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from app.services.learning_profile import categorize_failure
from app.services.mentor import MAX_TIER, TIERS

logger = logging.getLogger(__name__)

LEARNER_ACTIONS = ("submit", "hint", "quit")


class PracticeState(TypedDict, total=False):
    # --- fixed for the session (supplied on start) ---
    user_id: str
    problem_id: str
    language: str
    provider: str

    # --- latest learner input (from resume payloads) ---
    action: str                 # submit | hint | quit | invalid
    user_code: str
    reasoning: str
    hint_tier: int
    recalled_moment: str | None
    profile_summary: str

    # --- retrieval (LangChain) ---
    language_notes: list[str]   # general idioms/pitfalls for this language
    failure_notes: list[str]    # notes targeted at the latest failure

    # --- evaluation ---
    outcome: str                # passed | failed | unverified | blocked | ""
    analysis: dict | None
    evidence: dict | None
    failure_category: str
    failure_detail: str
    attempts: int

    # --- what the client should render after this step ---
    reply: str
    tier_label: str
    step_back: dict | None
    reflection: str


# --------------------------------------------------------------------------
# Dependencies
# --------------------------------------------------------------------------

@dataclass
class PracticeDeps:
    # (query, language) -> list of document texts
    retrieve_notes: Callable[[str, str], Awaitable[list[str]]]
    # (code, language) -> (allowed, learner-facing message)
    screen: Callable[[str, str], tuple[bool, str]]
    # (problem_id, code, language, provider) -> (analysis dict, evidence dict)
    review: Callable[[str, str, str, str], Awaitable[tuple[dict, dict]]]
    # keyword args mirror app.services.mentor.mentor_reply
    hint: Callable[..., Awaitable[str]]
    # problem_id -> step-back offer or None
    step_back: Callable[[str], dict | None]
    review_with_recall: Callable | None = None


def default_deps() -> PracticeDeps:
    """Real implementations. Imports are lazy so importing this module does
    not pull in Chroma, the sandbox or provider SDKs."""

    async def retrieve_notes(query: str, language: str) -> list[str]:
        from app.services.knowledge_base import get_vectorstore
        from app.services.curriculum_search import search

        def _search():
            local = search(query, "language", language, k=3)
            if local:
                return local
            where = {"$and": [{"track": "language"}, {"language": language}, {"contains_answer": False}]}
            return get_vectorstore().similarity_search(query, k=3, filter=where)

        try:
            docs = await asyncio.to_thread(_search)
        except Exception:
            # Retrieval is an enhancement; a hint without notes beats no hint.
            logger.warning("language-note retrieval failed", exc_info=True)
            return []
        from app.services.content_access import public_text
        return [public_text(d.page_content) for d in docs
                if d.metadata.get("contains_answer") is False
                and d.metadata.get("language") == language
                and d.metadata.get("track") == "language"
                and not str(d.metadata.get("problem_id", "")).startswith("upload:")
                and not d.metadata.get("document_id") and not d.metadata.get("user_id")]

    def screen(code: str, language: str) -> tuple[bool, str]:
        from app.services.code_screener import explain, screen as _screen

        result = _screen(code, language)
        return result.allowed, explain(result)

    async def review(problem_id: str, code: str, language: str,
                     provider: str, recalled_moment: str | None = None) -> tuple[dict, dict]:
        from app.services.deep_review import deep_review

        analysis, evidence = await deep_review(
            problem_id=problem_id, user_code=code,
            language=language, provider=provider,
            **({"recalled_moment": recalled_moment} if recalled_moment else {}),
        )
        # Checkpointed state must be plain data.
        return analysis.model_dump(), json.loads(json.dumps(evidence, default=str))

    async def hint(**kwargs: Any) -> str:
        from app.services.mentor import mentor_reply

        return await mentor_reply(**kwargs)

    def step_back(problem_id: str) -> dict | None:
        from app.services.content_catalog import filter_content
        from app.services.mentor import step_back_offer

        algorithms = next(
            (c.algorithms for c in filter_content() if c.id == problem_id), []
        )
        return step_back_offer(problem_id, algorithms)

    return PracticeDeps(retrieve_notes, screen, review, hint, step_back, review_with_recall=review)


# --------------------------------------------------------------------------
# Pure helpers (unit-testable without a graph)
# --------------------------------------------------------------------------

def classify_outcome(evidence: dict | None) -> tuple[str, str, str]:
    """(outcome, failure_category, failure_detail) from execution evidence.

    Stricter than routers/analyze.py on purpose: with no curated run and no
    fuzz run there is no evidence of correctness, so the result is
    "unverified" rather than a vacuous pass.
    """
    evidence = evidence or {}
    curated = evidence.get("curated") or {}
    tier1 = [r for r in curated.get("results", []) if r.get("tier") == 1]
    fuzz = evidence.get("fuzz") or {}
    category, detail = categorize_failure(evidence)

    if not tier1 and not fuzz.get("ran"):
        return "unverified", category, detail

    failed = (
        any(r.get("status") != "passed" for r in tier1)
        or bool(category)
        or bool(fuzz.get("counterexamples"))
        or (bool(fuzz.get("ran")) and fuzz.get("passed",0) < fuzz.get("total",0))
    )
    return ("failed" if failed else "passed"), category, detail


def parse_learner_payload(payload: Any) -> dict:
    """Validate a resume payload. It comes from an HTTP body, so it is
    untrusted: anything malformed becomes action="invalid" and loops back to
    await_learner with an explanation instead of raising mid-graph."""
    reset = {"step_back": None, "tier_label": ""}
    if not isinstance(payload, dict) or payload.get("action") not in LEARNER_ACTIONS:
        return {**reset, "action": "invalid",
                "reply": f"Expected an action, one of: {', '.join(LEARNER_ACTIONS)}."}

    action = payload["action"]
    if action == "submit":
        code = payload.get("code")
        if not isinstance(code, str) or not code.strip():
            return {**reset, "action": "invalid", "reply": "Submit needs non-empty code."}
        return {**reset, "action": "submit", "user_code": code, "recalled_moment": payload.get("recalled_moment")}

    if action == "hint":
        reasoning = payload.get("reasoning")
        tier = payload.get("hint_tier")
        if not isinstance(reasoning, str) or not reasoning.strip():
            # Pedagogy, not validation: the mentor responds to THEIR thinking.
            return {**reset, "action": "invalid",
                    "reply": "Tell me how you're thinking about it first, then I can help."}
        if not isinstance(tier, int):
            return {**reset, "action": "invalid", "reply": "hint_tier is required."}
        update = {**reset, "action": "hint", "reasoning": reasoning,
                  "hint_tier": max(1, min(tier, MAX_TIER)),
                  "recalled_moment": payload.get("recalled_moment"),
                  "profile_summary": payload.get("profile_summary") or ""}
        if isinstance(payload.get("code"), str):
            update["user_code"] = payload["code"]
        return update

    return {**reset, "action": "quit"}


# --------------------------------------------------------------------------
# Graph
# --------------------------------------------------------------------------

def build_practice_graph(checkpointer: Any, deps: PracticeDeps | None = None):
    """Compile the practice graph.

    `checkpointer` is required, not defaulted: interrupts only work with one,
    and silently falling back to in-memory storage would lose every session
    on restart and break with more than one worker. Use a Postgres/SQLite
    saver in the app and InMemorySaver in tests.
    """
    d = deps or default_deps()

    async def load_context(state: PracticeState) -> dict:
        lang, pid = state["language"], state["problem_id"]
        notes = await d.retrieve_notes(f"{lang} idioms and pitfalls for {pid}", lang)
        return {"language_notes": notes, "attempts": 0, "outcome": "",
                "reply": "", "failure_notes": []}

    def await_learner(state: PracticeState) -> dict:
        payload = interrupt({
            "awaiting": "learner",
            "accepts": list(LEARNER_ACTIONS),
            "outcome": state.get("outcome", ""),
            "reply": state.get("reply", ""),
            "tier_label": state.get("tier_label", ""),
            "step_back": state.get("step_back"),
            "attempts": state.get("attempts", 0),
        })
        return parse_learner_payload(payload)

    def screen(state: PracticeState) -> dict:
        allowed, message = d.screen(state["user_code"], state["language"])
        if allowed:
            return {"outcome": ""}
        # Defence in depth only. Strikes are recorded by the router, which
        # also screens before resuming, because that is a DB side effect.
        return {"outcome": "blocked", "reply": message}

    async def evaluate(state: PracticeState) -> dict:
        reviewer = d.review_with_recall or d.review
        options = {"recalled_moment": state.get("recalled_moment")} if d.review_with_recall else {}
        analysis, evidence = await reviewer(
            state["problem_id"], state["user_code"],
            state["language"], state["provider"], **options,
        )
        outcome, category, detail = classify_outcome(evidence)
        reply = ""
        if outcome == "unverified":
            reply = (f"Automated tests can't run {state['language']} for this "
                     "problem yet, so this review is based on reading the code only.")
        return {"analysis": analysis, "evidence": evidence, "outcome": outcome,
                "failure_category": category, "failure_detail": detail,
                "attempts": state.get("attempts", 0) + 1, "reply": reply,
                "failure_notes": []}

    async def diagnose(state: PracticeState) -> dict:
        # Targeted retrieval: e.g. a Go backtracking failure pulls the
        # slice-header aliasing note instead of generic Go material.
        lang = state["language"]
        query = f"{lang} {state.get('failure_category', '')} {state.get('failure_detail', '')}"
        return {"failure_notes": await d.retrieve_notes(query.strip(), lang)}

    async def mentor_hint(state: PracticeState) -> dict:
        tier = state["hint_tier"]
        notes = state.get("failure_notes") or state.get("language_notes") or []
        reply = await d.hint(
            problem_id=state["problem_id"],
            reasoning=state["reasoning"],
            current_code=state.get("user_code", ""),
            language=state["language"],
            tier=tier,
            provider=state["provider"],
            recalled_moment=state.get("recalled_moment"),
            profile_summary=state.get("profile_summary", ""),
            language_notes="\n\n---\n\n".join(notes),
        )
        return {"reply": reply, "tier_label": TIERS[tier][0]}

    def step_back(state: PracticeState) -> dict:
        return {"step_back": d.step_back(state["problem_id"])}

    def await_reflection(state: PracticeState) -> dict:
        payload = interrupt({
            "awaiting": "reflection",
            "outcome": "passed",
            "analysis": state.get("analysis"),
            "attempts": state.get("attempts", 0),
        })
        text = payload.get("reasoning", "") if isinstance(payload, dict) else ""
        return {"reflection": text if isinstance(text, str) else ""}

    # --- routing (pure functions of state) ---
    def route_learner(state: PracticeState) -> Literal["screen", "mentor_hint", "await_learner", "__end__"]:
        return {"submit": "screen", "hint": "mentor_hint", "quit": END}.get(
            state.get("action", ""), "await_learner")

    def route_screen(state: PracticeState) -> Literal["evaluate", "await_learner"]:
        return "await_learner" if state.get("outcome") == "blocked" else "evaluate"

    def route_evaluate(state: PracticeState) -> Literal["await_reflection", "diagnose", "await_learner"]:
        return {"passed": "await_reflection", "failed": "diagnose"}.get(
            state["outcome"], "await_learner")

    def route_hint(state: PracticeState) -> Literal["step_back", "await_learner"]:
        return "step_back" if state["hint_tier"] >= MAX_TIER else "await_learner"

    g = StateGraph(PracticeState)
    for name, fn in [
        ("load_context", load_context), ("await_learner", await_learner),
        ("screen", screen), ("evaluate", evaluate), ("diagnose", diagnose),
        ("mentor_hint", mentor_hint), ("step_back", step_back),
        ("await_reflection", await_reflection),
    ]:
        g.add_node(name, fn)

    g.add_edge(START, "load_context")
    g.add_edge("load_context", "await_learner")
    g.add_conditional_edges("await_learner", route_learner)
    g.add_conditional_edges("screen", route_screen)
    g.add_conditional_edges("evaluate", route_evaluate)
    g.add_edge("diagnose", "await_learner")
    g.add_conditional_edges("mentor_hint", route_hint)
    g.add_edge("step_back", "await_learner")
    g.add_edge("await_reflection", END)
    return g.compile(checkpointer=checkpointer)


# --------------------------------------------------------------------------
# Router helpers
# --------------------------------------------------------------------------

def thread_config(user_id: str, problem_id: str, session_id: str) -> dict:
    """Checkpoint key. The router must build this from the AUTHENTICATED
    user id, never from a client-supplied thread id, or one learner could
    resume another's session."""
    return {"configurable": {"thread_id": f"practice:{user_id}:{problem_id}:{session_id}"}}


def pending_interrupt(result: dict) -> dict | None:
    """The payload the graph is waiting on (what the client should render),
    or None if the session has finished."""
    interrupts = (result or {}).get("__interrupt__") or []
    return interrupts[0].value if interrupts else None
