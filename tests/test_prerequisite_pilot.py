"""The pilot graph is acyclic learning metadata, not a mastery gate."""
import json
from pathlib import Path

from app.core.config import Settings
from app.services.learning_path import SPINE
from app.services.prerequisite_graph import guidance, linked_content_ids


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
