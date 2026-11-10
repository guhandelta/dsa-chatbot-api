"""The pilot graph is acyclic learning metadata, not a mastery gate."""
import json
from pathlib import Path

from app.core.config import Settings
from app.services.learning_path import SPINE
import pytest

from app.services import prerequisite_graph as pilot
from app.services.prerequisite_graph import audit_language, guidance, linked_content_ids, validate_graph


def test_kag_pilot_is_off_unless_enabled():
    assert Settings.model_fields["kag_enabled"].default is False


def test_pilot_graph_matches_shared_spine_and_has_only_earlier_dependencies():
    path = Path(__file__).resolve().parents[1] / "data/curriculum/prerequisite-pilot.json"
    graph = json.loads(path.read_text())
    assert graph["status"] == "pilot-learning-metadata"
    nodes = graph["nodes"]
    assert [node["stage"] for node in nodes] == list(range(1, 9))
    spine = {stage.number: stage for stage in SPINE}
    for node in nodes:
        assert node["slug"] == spine[node["stage"]].slug
        assert len(node["requires"]) == len(set(node["requires"]))
        assert all(1 <= requirement < node["stage"] for requirement in node["requires"])


def test_links_resolve_only_for_the_selected_language():
    assert linked_content_ids("python", "python-path-07-maps") == ("python-path-06-arrays",)
    assert linked_content_ids("python", "python-path-07-maps", "What is a map?") == ()
    assert linked_content_ids("python", "python-path-07-maps", "How does an array help?") == ("python-path-06-arrays",)
    assert linked_content_ids("java", "python-path-07-maps") == ()
    assert guidance("python", "python-path-07-maps").startswith("Pilot prerequisite links")


def test_graph_rejects_malformed_and_unresolved_edges():
    original = json.loads((Path(__file__).resolve().parents[1] / "data/curriculum/prerequisite-pilot.json").read_text())
    assert len(validate_graph(original)) == 8
    broken = [None, {**original, "nodes": None},
              {**original, "version": 99},
              {**original, "nodes": [None]},
              {**original, "nodes": [{"stage": True, "slug": "values", "requires": []}]},
              {**original, "nodes": [{"stage": 2, "slug": "conditions", "requires": [1]}]}]
    for item in broken:
        with pytest.raises(ValueError):
            validate_graph(item)


def test_language_resolution_audit_is_read_only(monkeypatch):
    assert audit_language("python") == []
    assert audit_language("not-a-language") == ["unknown language: not-a-language"]
    monkeypatch.setattr("app.services.content_catalog.find_path", lambda content_id: None)
    assert "missing authored lesson: python-path-01-values" in audit_language("python")


def test_missing_or_invalid_graph_never_blocks_the_tutor(monkeypatch):
    assert guidance("python", None) == ""
    assert linked_content_ids("python", None) == ()
    assert guidance("java", "python-path-07-maps") == ""
    assert guidance("python", "python-path-01-values") == ""
    def broken():
        raise ValueError("invalid")
    monkeypatch.setattr(pilot, "graph", broken)
    assert guidance("python", "python-path-07-maps") == ""
    assert linked_content_ids("python", "python-path-07-maps") == ()
