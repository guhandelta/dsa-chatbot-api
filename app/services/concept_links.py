"""Validate draft cross-section learning links; no runtime access or mastery effect."""

import json
from pathlib import Path

from app.services.content_catalog import SECTIONS, find_path, list_content

PILOT_PATH = Path(__file__).resolve().parents[2] / "data/curriculum/connected-route-pilot.json"
SECTION_IDS = frozenset(SECTIONS)
LINK_TYPES = frozenset({"requires", "uses", "applies"})
REVIEW_STATES = frozenset({"pending", "missing-content", "draft-only", "reviewed"})


def validate(data: dict) -> dict:
    """Reject unresolved IDs, malformed metadata, and prerequisite cycles."""
    if not isinstance(data, dict) or data.get("version") != 1 or data.get("status") != "draft-advisory":
        raise ValueError("unsupported concept map")
    nodes, links = data.get("nodes"), data.get("links")
    if not isinstance(nodes, list) or not isinstance(links, list) or not nodes:
        raise ValueError("invalid concept map lists")
    by_id = {}
    for node in nodes:
        if not isinstance(node, dict):
            raise ValueError("invalid concept node")
        identifier, section, content_id, review = (node.get(k) for k in ("id", "section", "content_id", "review"))
        if (not isinstance(section, str) or section not in SECTION_IDS
                or not isinstance(identifier, str) or not identifier.startswith(f"{section}:")
                or identifier in by_id or not isinstance(review, str) or review not in REVIEW_STATES
                or (content_id is not None and (not isinstance(content_id, str) or not find_path(content_id)))):
            raise ValueError("invalid concept node")
        if content_id is None and review != "missing-content":
            raise ValueError("missing content needs explicit review state")
        if content_id is not None:
            content = next((item for item in list_content() if item.id == content_id), None)
            if content is None or content.track not in SECTIONS[section]:
                raise ValueError("concept content belongs to another section")
        by_id[identifier] = node
    requires = {identifier: set() for identifier in by_id}
    seen = set()
    for link in links:
        if not isinstance(link, dict):
            raise ValueError("invalid concept link")
        source, target, kind, review = (link.get(k) for k in ("from", "to", "type", "review"))
        key = (source, target, kind)
        if (not isinstance(source, str) or not isinstance(target, str) or source not in by_id
                or target not in by_id or source == target or not isinstance(kind, str)
                or kind not in LINK_TYPES or not isinstance(review, str)
                or review not in {"pending", "reviewed"} or key in seen):
            raise ValueError("invalid concept link")
        seen.add(key)
        if kind == "requires":
            requires[source].add(target)
    visiting, visited = set(), set()

    def visit(identifier: str) -> None:
        if identifier in visiting:
            raise ValueError("cyclic prerequisite links")
        if identifier in visited:
            return
        visiting.add(identifier)
        for target in requires[identifier]:
            visit(target)
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in requires:
        visit(identifier)
    return data


def pilot() -> dict:
    return validate(json.loads(PILOT_PATH.read_text(encoding="utf-8")))
