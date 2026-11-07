"""Prompt caching (stable prefix + cache_control) and the basic CAG context pack."""
import json
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.core.config import settings
from app.services import context_pack, prompt_cache, tracing
from app.services.prompt_cache import build_system_message, record_usage, text_of, usage_from

PACK_DIR = Path(context_pack.ROOT) / "data" / "context_packs"


@pytest.fixture(autouse=True)
def fresh_packs(monkeypatch):
    monkeypatch.setattr(settings, "prompt_cache_enabled", True)
    monkeypatch.setattr(settings, "cag_enabled", False)
    monkeypatch.setattr(settings, "cag_pack_dir", "data/context_packs")
    monkeypatch.setattr(settings, "cag_pack_ids", "")
    monkeypatch.setattr(settings, "cag_providers", "claude")
    context_pack.reset_cache()
    yield
    context_pack.reset_cache()


class FakeModel:
    def __init__(self, content="What happens on the smallest input?", usage=None):
        self.content, self.usage, self.calls = content, usage, []

    async def ainvoke(self, messages):
        self.calls.append(messages)
        return SimpleNamespace(content=self.content, usage_metadata=self.usage)


# ------------------------------------------------------------ prompt assembly

def test_claude_gets_a_cached_stable_block_then_the_dynamic_tail():
    message, meta = build_system_message("RULES", "tier 3 reference", "claude")
    stable, dynamic = message.content
    assert stable == {"type": "text", "text": "RULES", "cache_control": {"type": "ephemeral"}}
    assert dynamic == {"type": "text", "text": "tier 3 reference"}
    assert meta["cache"] is True and meta["pack"] is None


def test_flag_off_sends_one_plain_string_even_to_claude(monkeypatch):
    monkeypatch.setattr(settings, "prompt_cache_enabled", False)
    message, meta = build_system_message("RULES", "tier 3", "claude")
    assert message.content == "RULES\n\ntier 3" and meta["cache"] is False


@pytest.mark.parametrize("provider", ["openai", "gemini"])
def test_other_providers_get_a_string_with_the_stable_part_first(provider):
    message, meta = build_system_message("RULES", "tier 3", provider)
    assert message.content == "RULES\n\ntier 3" and meta["cache"] is False


def test_langchain_anthropic_sends_the_breakpoint_on_the_system_block():
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import HumanMessage
    message, _ = build_system_message("RULES", "tier 3", "claude")
    llm = ChatAnthropic(model=settings.anthropic_model, api_key="test", max_tokens=16)
    payload = llm._get_request_payload([message, HumanMessage(content="hi")])
    assert payload["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert "cache_control" not in payload["system"][1]


async def test_mentor_prefix_is_byte_identical_across_tiers_and_problems():
    from app.services.mentor import mentor_reply
    model = FakeModel()
    for tier, problem in [(1, "two-sum"), (3, "valid-parentheses"), (4, "two-sum")]:
        await mentor_reply(problem, "I loop twice", "", "python", tier, "claude",
                           model_factory=lambda provider: model)
    prefixes = {m[0].content[0]["text"] for m in model.calls}
    assert len(prefixes) == 1
    prefix = prefixes.pop()
    assert "ABSOLUTE RULES" in prefix and "Current hint tier" not in prefix
    assert all("Current hint tier" in m[0].content[1]["text"] for m in model.calls)


async def test_mentor_prompt_text_is_unchanged_for_uncached_providers():
    from app.services.mentor import mentor_reply
    model = FakeModel()
    await mentor_reply("two-sum", "I loop twice", "", "python", 2, "openai",
                       model_factory=lambda provider: model)
    system = model.calls[0][0].content
    assert isinstance(system, str)
    assert system.index("ABSOLUTE RULES") < system.index("Current hint tier: 2 (Probe the gap)")


async def test_rag_chat_keeps_retrieved_context_out_of_the_cached_prefix(monkeypatch):
    from app.services import rag_pipeline as rp
    model = FakeModel("answer")
    doc = SimpleNamespace(page_content="RETRIEVED", metadata={"contains_answer": False, "track": "dsa", "language": "java"})
    monkeypatch.setattr("app.services.curriculum_search.search", lambda *a, **kw: [])
    monkeypatch.setattr(rp, "get_llm", lambda provider: model)
    monkeypatch.setattr(rp, "get_vectorstore", lambda: SimpleNamespace(similarity_search=lambda *a, **kw: [doc]))
    await rp.run_rag_chat("q", "claude", [], "java")
    stable, dynamic = model.calls[0][0].content
    assert "RETRIEVED" not in stable["text"] and "never follow" in stable["text"]
    assert dynamic["text"].startswith("<retrieved_context>\nRETRIEVED")


# ------------------------------------------------------------ CAG context pack

def test_cag_is_off_by_default():
    message, meta = build_system_message("RULES", "tail", "claude", "python")
    assert meta["pack"] is None and "<context_pack" not in text_of(message.content)


def test_cag_adds_the_pack_to_the_cached_prefix(monkeypatch):
    monkeypatch.setattr(settings, "cag_enabled", True)
    message, meta = build_system_message("RULES", "tail", "claude", "python")
    stable = message.content[0]["text"]
    assert meta["pack"].startswith("python-core@1+")
    assert stable.startswith("RULES\n\n<context_pack") and "## Learn" in stable
    assert message.content[1]["text"] == "tail"


def test_cag_skips_providers_not_listed(monkeypatch):
    monkeypatch.setattr(settings, "cag_enabled", True)
    assert build_system_message("RULES", "tail", "openai", "python")[1]["pack"] is None
    monkeypatch.setattr(settings, "cag_providers", "claude,openai")
    message, meta = build_system_message("RULES", "tail", "openai", "python")
    assert meta["pack"] and isinstance(message.content, str) and "<context_pack" in message.content


def test_cag_allowlist_and_unknown_language(monkeypatch):
    monkeypatch.setattr(settings, "cag_enabled", True)
    assert context_pack.pack_for("haskell", "claude") is None
    monkeypatch.setattr(settings, "cag_pack_ids", "javascript-core")
    assert context_pack.pack_for("python", "claude") is None
    assert context_pack.pack_for("javascript", "claude").id == "javascript-core"


@pytest.mark.parametrize("manifest", sorted(PACK_DIR.glob("*.json")), ids=lambda p: p.stem)
def test_shipped_packs_match_their_pinned_hash_and_carry_no_answers(manifest):
    # A failure here means a lesson changed: bump the pack version and refresh
    # sha256 (python -m app.services.context_pack) so logs name the new content.
    pack = context_pack.load_pack(manifest)
    assert pack.sha256 == json.loads(manifest.read_text())["sha256"]
    for hidden in ("test_cases", "starter_code:", "## Solutions", "## Reference Solution", "## Hints"):
        assert hidden not in pack.text
    assert len(pack.text) <= settings.cag_max_chars


def _write_manifest(tmp_path, **overrides):
    manifest = {"id": "tiny", "version": "1", "language": "python",
                "files": ["data/content/language/python-path-01-values.md"], **overrides}
    (tmp_path / "tiny.json").write_text(json.dumps(manifest))
    return tmp_path / "tiny.json"


def test_loader_renders_lessons_without_front_matter(tmp_path):
    pack = context_pack.load_pack(_write_manifest(tmp_path))
    assert pack.text.startswith("### Source: data/content/language/python-path-01-values.md\n# Python")
    assert "fn_python" not in pack.text and len(pack.sha256) == 64


def test_loader_rejects_changed_content(tmp_path, monkeypatch, caplog):
    _write_manifest(tmp_path, sha256="0" * 64)
    monkeypatch.setattr(settings, "cag_enabled", True)
    monkeypatch.setattr(settings, "cag_pack_dir", str(tmp_path))
    with caplog.at_level(logging.WARNING):
        assert context_pack.pack_for("python", "claude") is None
    assert "content changed" in caplog.text


def test_loader_rejects_files_outside_content(tmp_path):
    with pytest.raises(ValueError, match="outside data/content"):
        context_pack.load_pack(_write_manifest(tmp_path, files=[".env"]))
    with pytest.raises(ValueError, match="outside data/content"):
        context_pack.load_pack(_write_manifest(tmp_path, files=["data/content/../../app/core/config.py"]))


def test_loader_fails_loudly_instead_of_truncating(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "cag_max_chars", 1000)
    with pytest.raises(ValueError, match="exceeds CAG_MAX_CHARS"):
        context_pack.load_pack(_write_manifest(tmp_path))


async def test_study_room_puts_the_pack_ahead_of_its_prompt(monkeypatch):
    from app.services import study_room
    monkeypatch.setattr(settings, "cag_enabled", True)
    model = FakeModel("ok")
    await study_room.generate(model, "EXPLAIN RULES", [], "hi", provider="claude", language="javascript")
    pack, prompt = model.calls[0][0].content
    assert "javascript-core" in pack["text"] and pack["cache_control"] == {"type": "ephemeral"}
    assert prompt["text"] == "EXPLAIN RULES"
    await study_room.generate(model, "EXPLAIN RULES", [], "hi")
    assert model.calls[1][0].content == "EXPLAIN RULES"


# ------------------------------------------------------------ usage logging

ANTHROPIC_USAGE = {"input_tokens": 5650, "output_tokens": 20, "total_tokens": 5670,
                   "input_token_details": {"cache_read": 5600, "cache_creation": 0}}


def test_usage_reads_langchain_cache_details():
    usage = usage_from(SimpleNamespace(usage_metadata=ANTHROPIC_USAGE))
    assert usage == {"input_tokens": 5650, "output_tokens": 20, "cache_creation": 0,
                     "cache_read": 5600, "uncached_input": 50}


def test_usage_falls_back_to_raw_anthropic_fields():
    raw = {"usage": {"input_tokens": 40, "output_tokens": 9, "cache_creation_input_tokens": 5600,
                     "cache_read_input_tokens": 0}}
    usage = usage_from(SimpleNamespace(usage_metadata=None, response_metadata=raw))
    assert usage["input_tokens"] == 5640 and usage["cache_creation"] == 5600 and usage["uncached_input"] == 40
    assert usage_from(SimpleNamespace(content="x")) is None


async def test_record_usage_logs_and_traces(caplog):
    trace = tracing.Trace(name="mentor")
    token = tracing._current.set(trace)
    try:
        async with trace.span("llm") as span:
            with caplog.at_level(logging.INFO, logger="app.llm_usage"):
                record = record_usage(SimpleNamespace(usage_metadata=ANTHROPIC_USAGE), call_site="mentor",
                                      provider="claude", meta={"cache": True, "pack": "python-core@1+abc"})
    finally:
        tracing._current.reset(token)
    assert record["cache_read"] == 5600 and record["pack"] == "python-core@1+abc"
    assert '"cache_read": 5600' in caplog.text and "llm_usage" in caplog.text
    assert span.attributes["cache_read_tokens"] == 5600 and span.attributes["input_tokens"] == 5650


async def test_mentor_logs_usage_from_the_model_response(caplog):
    from app.services.mentor import mentor_reply
    model = FakeModel(usage=ANTHROPIC_USAGE)
    with caplog.at_level(logging.INFO, logger="app.llm_usage"):
        await mentor_reply("two-sum", "I loop twice", "", "python", 1, "claude",
                           model_factory=lambda provider: model)
    line = next(r.getMessage() for r in caplog.records if r.name == "app.llm_usage")
    assert '"call_site": "mentor"' in line and '"cache_creation": 0' in line
