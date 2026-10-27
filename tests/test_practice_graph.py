# Practice graph: routing, interrupts/resume, and the real-mentor path.
#
# The app's real LLM (app.services.llm_router.get_llm) is replaced here only
# so tests are free, deterministic and need no API keys. In production the
# graph's default_deps() call the real deep_review / mentor_reply / Chroma.
import pytest
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.graphs.practice import (
    PracticeDeps,
    build_practice_graph,
    classify_outcome,
    parse_learner_payload,
    pending_interrupt,
    thread_config,
)
from app.services.mentor import MAX_TIER

PASS_EVIDENCE = {"curated": {"results": [
    {"tier": 1, "status": "passed", "passed_cases": 5, "total_cases": 5, "detail": ""}]},
    "fuzz": {"ran": True, "passed": 200, "total": 200, "counterexamples": []}}
FAIL_EVIDENCE = {"curated": {"results": [
    {"tier": 1, "status": "failed", "passed_cases": 3, "total_cases": 5, "detail": "case 4"}]},
    "fuzz": {"ran": True, "passed": 150, "total": 200, "counterexamples": [
        {"args": [[]], "student_output": None, "reference_output": 0,
         "description": "empty"}]}}


# ---------------- pure helpers ----------------

def test_no_evidence_is_unverified_not_a_pass():
    assert classify_outcome({"curated": None, "fuzz": None})[0] == "unverified"


def test_outcome_from_evidence():
    assert classify_outcome(PASS_EVIDENCE)[0] == "passed"
    outcome, category, _ = classify_outcome(FAIL_EVIDENCE)
    assert outcome == "failed" and category == "empty_input"


@pytest.mark.parametrize("payload", [
    None, "submit", {"action": "delete_everything"},
    {"action": "submit", "code": "   "},
    {"action": "hint", "hint_tier": 1},                # no reasoning
    {"action": "hint", "reasoning": "x", "hint_tier": "2"},
])
def test_malformed_payloads_become_invalid(payload):
    assert parse_learner_payload(payload)["action"] == "invalid"


def test_hint_tier_is_clamped():
    assert parse_learner_payload(
        {"action": "hint", "reasoning": "x", "hint_tier": 99})["hint_tier"] == MAX_TIER


def test_next_submission_clears_earlier_project_files():
    project = parse_learner_payload({"action": "submit", "code": "method",
                                     "files": {"Main.java": "method", "Helper.java": "class Helper {}"}})
    assert project["project_files"]["Helper.java"] == "class Helper {}"
    assert parse_learner_payload({"action": "submit", "code": "new method"})["project_files"] is None


# ---------------- graph with fake deps ----------------

class Fakes:
    """Records calls so tests can assert what the graph did."""

    def __init__(self, reviews):
        self.reviews = list(reviews)
        self.calls: dict[str, list] = {"retrieve": [], "review": [], "hint": [], "step_back": []}
        self.blocked = False

    async def retrieve_notes(self, query, language):
        self.calls["retrieve"].append(query)
        return [f"NOTE[{query}]"]

    def screen(self, code, language):
        return (not self.blocked, "blocked: no filesystem access" if self.blocked else "")

    async def review(self, problem_id, code, language, provider):
        self.calls["review"].append(code)
        return {"summary": "review"}, self.reviews.pop(0)

    async def hint(self, **kw):
        self.calls["hint"].append(kw)
        return f"hint tier {kw['tier']}"

    def step_back(self, problem_id):
        self.calls["step_back"].append(problem_id)
        return {"algorithm": "two-pointers", "message": "step back"}

    def deps(self):
        return PracticeDeps(self.retrieve_notes, self.screen, self.review,
                            self.hint, self.step_back)


START = {"user_id": "u1", "problem_id": "two-sum", "language": "go", "provider": "gemini"}


async def _start(fakes):
    graph = build_practice_graph(InMemorySaver(), fakes.deps())
    cfg = thread_config("u1", "two-sum", "s1")
    first = await graph.ainvoke(START, cfg)
    return graph, cfg, first


async def test_fail_hint_resubmit_pass_reflect():
    fakes = Fakes([FAIL_EVIDENCE, PASS_EVIDENCE])
    graph, cfg, first = await _start(fakes)
    assert pending_interrupt(first)["awaiting"] == "learner"

    r = await graph.ainvoke(Command(resume={"action": "submit", "code": "v1"}), cfg)
    assert pending_interrupt(r)["outcome"] == "failed"

    r = await graph.ainvoke(Command(resume={
        "action": "hint", "reasoning": "I loop over pairs", "hint_tier": 1}), cfg)
    assert pending_interrupt(r)["reply"] == "hint tier 1"
    # the hint was grounded in failure-targeted retrieval, not generic notes
    assert "empty_input" in fakes.calls["hint"][0]["language_notes"]
    assert fakes.calls["hint"][0]["current_code"] == "v1"

    r = await graph.ainvoke(Command(resume={"action": "submit", "code": "v2"}), cfg)
    assert pending_interrupt(r)["awaiting"] == "reflection"

    r = await graph.ainvoke(Command(resume={"reasoning": "hash map of complements"}), cfg)
    assert pending_interrupt(r) is None                      # session finished
    assert r["reflection"] == "hash map of complements"
    assert r["attempts"] == 2
    assert fakes.calls["review"] == ["v1", "v2"]


async def test_graph_passes_native_project_then_clears_it_on_plain_resubmit():
    fakes = Fakes([])
    received = []

    async def review(problem_id, code, language, provider, *, recalled_moment=None, files=None):
        received.append(files)
        return {"summary": "review"}, FAIL_EVIDENCE if len(received) == 1 else PASS_EVIDENCE

    deps = fakes.deps()
    deps.review_with_recall = review
    graph = build_practice_graph(InMemorySaver(), deps)
    cfg = thread_config("u1", "two-sum", "native-project")
    await graph.ainvoke(START, cfg)
    project = {"Main.java": "method", "Helper.java": "class Helper {}"}
    await graph.ainvoke(Command(resume={"action": "submit", "code": "method", "files": project}), cfg)
    await graph.ainvoke(Command(resume={"action": "submit", "code": "new method"}), cfg)
    assert received == [project, None]


async def test_resume_does_not_rerun_earlier_nodes():
    fakes = Fakes([FAIL_EVIDENCE])
    graph, cfg, _ = await _start(fakes)
    await graph.ainvoke(Command(resume={"action": "submit", "code": "v1"}), cfg)
    await graph.ainvoke(Command(resume={"action": "hint", "reasoning": "r", "hint_tier": 1}), cfg)
    # load_context ran once, diagnose once — the checkpoint carried state forward
    assert len(fakes.calls["retrieve"]) == 2
    assert len(fakes.calls["review"]) == 1


async def test_blocked_code_is_never_evaluated():
    fakes = Fakes([])
    fakes.blocked = True
    graph, cfg, _ = await _start(fakes)
    r = await graph.ainvoke(Command(resume={"action": "submit", "code": "import os"}), cfg)
    payload = pending_interrupt(r)
    assert payload["outcome"] == "blocked" and "filesystem" in payload["reply"]
    assert fakes.calls["review"] == []


async def test_unverified_language_does_not_reach_reflection():
    fakes = Fakes([{"curated": None, "fuzz": None, "complexity": None}])
    graph, cfg, _ = await _start(fakes)
    r = await graph.ainvoke(Command(resume={"action": "submit", "code": "func f() {}"}), cfg)
    payload = pending_interrupt(r)
    assert payload["awaiting"] == "learner" and payload["outcome"] == "unverified"
    assert "can't run go" in payload["reply"].lower()


async def test_top_tier_offers_step_back_not_answer():
    fakes = Fakes([])
    graph, cfg, _ = await _start(fakes)
    r = await graph.ainvoke(Command(resume={
        "action": "hint", "reasoning": "still stuck", "hint_tier": MAX_TIER}), cfg)
    payload = pending_interrupt(r)
    assert payload["step_back"]["algorithm"] == "two-pointers"
    # next action clears the stale offer
    r = await graph.ainvoke(Command(resume={"action": "hint", "reasoning": "ok", "hint_tier": 1}), cfg)
    assert pending_interrupt(r)["step_back"] is None


async def test_invalid_then_quit():
    fakes = Fakes([])
    graph, cfg, _ = await _start(fakes)
    r = await graph.ainvoke(Command(resume={"action": "nope"}), cfg)
    assert "expected an action" in pending_interrupt(r)["reply"].lower()
    r = await graph.ainvoke(Command(resume={"action": "quit"}), cfg)
    assert pending_interrupt(r) is None


async def test_sessions_are_isolated_by_thread():
    fakes = Fakes([FAIL_EVIDENCE])
    graph = build_practice_graph(InMemorySaver(), fakes.deps())
    a, b = thread_config("u1", "two-sum", "s1"), thread_config("u2", "two-sum", "s1")
    await graph.ainvoke(START, a)
    await graph.ainvoke({**START, "user_id": "u2"}, b)
    await graph.ainvoke(Command(resume={"action": "submit", "code": "v1"}), a)
    assert (await graph.aget_state(a)).values["attempts"] == 1
    assert (await graph.aget_state(b)).values["attempts"] == 0


# ---------------- real mentor_reply, fake chat model ----------------

class RecordingChatModel:
    """Stands in for the object get_llm() returns; captures the prompt."""

    def __init__(self):
        self.messages = None

    async def ainvoke(self, messages):
        self.messages = messages
        return AIMessage(content="What happens to `path` after you append it?")


async def test_graph_drives_the_real_mentor_with_language_notes(monkeypatch):
    model = RecordingChatModel()
    monkeypatch.setattr("app.services.mentor.get_llm", lambda provider: model)

    fakes = Fakes([FAIL_EVIDENCE])
    from app.graphs.practice import default_deps
    real_hint = default_deps().hint                 # the production hint path
    deps = PracticeDeps(fakes.retrieve_notes, fakes.screen, fakes.review,
                        real_hint, fakes.step_back)

    graph = build_practice_graph(InMemorySaver(), deps)
    cfg = thread_config("u1", "two-sum", "s1")
    await graph.ainvoke(START, cfg)
    await graph.ainvoke(Command(resume={"action": "submit", "code": "v1"}), cfg)
    r = await graph.ainvoke(Command(resume={
        "action": "hint", "reasoning": "I append path to res", "hint_tier": 2}), cfg)

    assert pending_interrupt(r)["reply"].startswith("What happens")
    system = model.messages[0].content
    assert "LANGUAGE PITFALLS" in system and "empty_input" in system
    assert "never state the fix" in system
    assert "Current hint tier: 2" in system
