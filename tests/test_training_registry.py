"""Tests for the Training Registry and Audit Log service, endpoints, and CLI tool."""
import json
from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services import training_registry


@pytest.mark.asyncio
async def test_training_registry_summary_structure():
    reg = training_registry.get_training_registry()
    assert reg["status"] == "ok"
    summary = reg["summary"]
    assert summary["total_technologies_trained"] >= 20
    assert summary["total_knowledge_records"] > 10000
    assert summary["total_retrievable_chunks"] > 8000
    assert summary["vector_store"]["status"] in ("active", "unavailable")

    categories = reg["categories"]
    assert "web_frontend" in categories
    assert "backend_frameworks" in categories
    assert "core_languages" in categories
    assert "embedded_systems" in categories

    tech_ids = {t["id"] for t in reg["technologies"]}
    assert "html" in tech_ids
    assert "css" in tech_ids
    assert "tailwind" in tech_ids
    assert "python-django" in tech_ids
    assert "rust" in tech_ids
    assert "java" in tech_ids
    assert "javascript" in tech_ids


@pytest.mark.asyncio
async def test_get_trained_technologies_list():
    techs = training_registry.get_trained_technologies()
    assert isinstance(techs, list)
    assert len(techs) >= 20

    html_item = next((t for t in techs if t["id"] == "html"), None)
    assert html_item is not None
    assert html_item["category"] == "web_frontend"
    assert html_item["records"] > 0
    assert html_item["retrievable"] > 0

    css_item = next((t for t in techs if t["id"] == "css"), None)
    assert css_item is not None
    assert css_item["category"] == "web_frontend"
    assert css_item["records"] > 0


@pytest.mark.asyncio
async def test_record_training_event_and_history(tmp_path, monkeypatch):
    test_log = tmp_path / "test_training_log.json"
    monkeypatch.setattr(training_registry, "LOG_FILE", test_log)

    event = training_registry.record_training_event(
        technology="svelte",
        action="new_framework_train",
        category="web_frontend",
        source="Training Data/language/svelte",
        record_count=150,
        vectors_count=150,
        status="completed",
        details={"framework_version": "5.0"},
    )
    assert event["technology"] == "svelte"
    assert event["record_count"] == 150
    assert event["status"] == "completed"

    history = training_registry.get_training_history(limit=10)
    assert len(history) >= 1
    assert history[0]["technology"] == "svelte"
    assert history[0]["details"]["framework_version"] == "5.0"

    limited = training_registry.get_training_history(limit=1)
    assert len(limited) == 1


@pytest.mark.asyncio
async def test_non_list_and_corrupted_log_file_resilience(tmp_path, monkeypatch):
    # Case 1: Corrupted non-JSON
    corrupted_log = tmp_path / "corrupted_log.json"
    corrupted_log.write_text("invalid json content {{{")
    monkeypatch.setattr(training_registry, "LOG_FILE", corrupted_log)

    history = training_registry.get_training_history()
    assert isinstance(history, list)
    assert len(history) > 0  # Falls back to seeded bootstrap events

    # Case 2: Valid JSON but not a list (e.g. dict)
    dict_log = tmp_path / "dict_log.json"
    dict_log.write_text(json.dumps({"not": "a list"}))
    monkeypatch.setattr(training_registry, "LOG_FILE", dict_log)

    history2 = training_registry.get_training_history()
    assert history2 == []


@pytest.mark.asyncio
async def test_manifest_read_failure_resilience(tmp_path, monkeypatch):
    fake_data = tmp_path / "data"
    (fake_data / "curriculum").mkdir(parents=True)
    (fake_data / "reference_library").mkdir(parents=True)

    # Write broken JSON in manifests
    (fake_data / "curriculum" / "manifest.json").write_text("invalid json {{{")
    (fake_data / "reference_library" / "manifest.json").write_text("invalid json {{{")

    monkeypatch.setattr(training_registry, "DATA_DIR", fake_data)

    reg = training_registry.get_training_registry()
    assert reg["status"] == "ok"
    assert "summary" in reg


@pytest.mark.asyncio
async def test_vectorstore_failure_resilience(monkeypatch):
    from app.services import knowledge_base
    def broken_vs():
        raise RuntimeError("Vector store connection timed out")
    monkeypatch.setattr(knowledge_base, "get_vectorstore", broken_vs)

    reg = training_registry.get_training_registry()
    assert reg["status"] == "ok"
    assert reg["summary"]["vector_store"]["status"] == "unavailable"
    assert "Vector store connection timed out" in reg["summary"]["vector_store"]["error"]


@pytest.mark.asyncio
async def test_api_endpoints_allow_admin(client, db):
    from app.db.models import User
    body=(await client.post("/auth/register",json={"email":"registry@scope.example","password":"password123"})).json()
    user=await db.get(User,body["user"]["id"]);user.role="admin";await db.commit()
    headers={"Authorization":"Bearer "+body["access_token"]}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        # 1. Full registry endpoint
        res = await client.get("/training/registry")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert "summary" in data
        assert "technologies" in data
        assert any(t["id"] == "html" for t in data["technologies"])

        # 2. History log endpoint
        res_hist = await client.get("/training/registry/history?limit=5")
        assert res_hist.status_code == 200
        hist_data = res_hist.json()
        assert isinstance(hist_data, list)
        assert len(hist_data) <= 5

        # 3. Technologies list endpoint
        res_tech = await client.get("/training/registry/technologies")
        assert res_tech.status_code == 200
        tech_data = res_tech.json()
        assert isinstance(tech_data, list)
        assert any(t["id"] == "html" for t in tech_data)
        assert any(t["id"] == "css" for t in tech_data)


def test_cli_tool_execution(capsys, monkeypatch):
    from tools import training_registry as cli

    # Test standard formatted report
    monkeypatch.setattr("sys.argv", ["training_registry.py"])
    cli.main()
    captured = capsys.readouterr().out
    assert "RAG CHATBOT — TRAINED TECHNOLOGIES & KNOWLEDGE REGISTRY" in captured
    assert "HTML5" in captured
    assert "CSS3" in captured

    # Test --json flag
    monkeypatch.setattr("sys.argv", ["training_registry.py", "--json"])
    cli.main()
    json_out = capsys.readouterr().out
    parsed = json.loads(json_out)
    assert parsed["status"] == "ok"

    # Test --history flag
    monkeypatch.setattr("sys.argv", ["training_registry.py", "--history"])
    cli.main()
    hist_out = capsys.readouterr().out
    parsed_hist = json.loads(hist_out)
    assert isinstance(parsed_hist, list)

    # Test --technologies flag
    monkeypatch.setattr("sys.argv", ["training_registry.py", "--technologies"])
    cli.main()
    tech_out = capsys.readouterr().out
    parsed_tech = json.loads(tech_out)
    assert isinstance(parsed_tech, list)


def test_cli_empty_events_and_long_name(capsys, monkeypatch):
    from tools import training_registry as cli

    # Empty events output
    def fake_empty_registry():
        reg = training_registry.get_training_registry()
        reg["recent_training_events"] = []
        reg["technologies"].append({
            "id": "very-long-tech-id-exceeding-thirty-characters",
            "display_name": "A Very Long Framework Display Name That Exceeds Thirty Characters For Formatting Test",
            "category": "web_frontend",
            "total_records": 999,
            "retrievable_records": 999,
        })
        return reg

    monkeypatch.setattr(cli, "get_training_registry", fake_empty_registry)
    monkeypatch.setattr("sys.argv", ["training_registry.py"])
    cli.main()
    out = capsys.readouterr().out
    assert "(No training events recorded yet)" in out
    assert "A Very Long Framework Displ..." in out
