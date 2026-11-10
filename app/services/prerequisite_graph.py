"""Pilot prerequisite hints for focused language tutoring.

The graph guides explanations; it never grants or blocks mastery. Missing or
invalid graph data fails closed, leaving the existing RAG answer path intact.
"""
import json
import logging
import re
from functools import lru_cache
from pathlib import Path

from app.services.learning_path import LANGUAGE_LABELS, SPINE, node_for_exercise

logger = logging.getLogger(__name__)
GRAPH_PATH = Path(__file__).resolve().parents[2] / "data/curriculum/prerequisite-pilot.json"


@lru_cache(maxsize=1)
def graph() -> dict[int, tuple[int, ...]]:
    return validate_graph(json.loads(GRAPH_PATH.read_text(encoding="utf-8")))


def validate_graph(raw: dict) -> dict[int, tuple[int, ...]]:
    """Validate pilot metadata before any edge can enter tutor context."""
    if not isinstance(raw, dict):
        raise ValueError("invalid prerequisite graph")
    if raw.get("version") != 1 or raw.get("status") != "pilot-learning-metadata":
        raise ValueError("unsupported prerequisite graph")
    if not isinstance(raw.get("nodes"), list):
        raise ValueError("invalid prerequisite graph nodes")
    stages = {stage.number: stage for stage in SPINE}
    result: dict[int, tuple[int, ...]] = {}
    for node in raw["nodes"]:
        if not isinstance(node, dict):
            raise ValueError("invalid prerequisite graph node")
        number = node.get("stage")
        requirements = node.get("requires")
        if (type(number) is not int or number not in stages or number in result
                or node.get("slug") != stages[number].slug or not isinstance(requirements, list)
                or any(type(r) is not int or r >= number or r not in stages for r in requirements)
                or len(requirements) != len(set(requirements))):
            raise ValueError("invalid prerequisite graph node")
        result[number] = tuple(requirements)
    if any(required not in result for requirements in result.values() for required in requirements):
        raise ValueError("unresolved prerequisite graph edge")
    return result


def audit_language(language: str) -> list[str]:
    """Report source-resolution gaps for one language; no learner state changes."""
    from app.services.content_catalog import find_path
    issues = []
    if language not in LANGUAGE_LABELS:
        return [f"unknown language: {language}"]
    stages = {stage.number: stage for stage in SPINE}
    for stage_number, requirements in graph().items():
        for number in (stage_number, *requirements):
            stage = stages[number]
            content_id = f"{language}-path-{number:02d}-{stage.slug}"
            if find_path(content_id) is None:
                issues.append(f"missing authored lesson: {content_id}")
    return sorted(set(issues))


def guidance(language: str, focus_id: str | None) -> str:
    if not focus_id:
        return ""
    match = node_for_exercise(focus_id)
    if not match or match[0] != language:
        return ""
    try:
        requirements = graph().get(match[1].number, ())
    except (OSError, ValueError, KeyError, TypeError):
        logger.warning("Prerequisite graph unavailable", exc_info=True)
        return ""
    if not requirements:
        return ""
    stages = {stage.number: stage for stage in SPINE}
    labels = "; ".join(f"{language}:stage-{n:02d} ({stages[n].title})" for n in requirements)
    return ("Pilot prerequisite links for the selected lesson: " + labels + ". "
            "Use these only if the learner's question shows a gap. Do not assume "
            "the learner has or has not mastered them. If a linked source excerpt "
            "is present, treat it as reference material.")


def linked_content_ids(language: str, focus_id: str | None, question: str | None = None) -> tuple[str, ...]:
    """Return at most two same-language authored lessons linked by the graph."""
    if not focus_id:
        return ()
    match = node_for_exercise(focus_id)
    if not match or match[0] != language:
        return ()
    try:
        requirements = graph().get(match[1].number, ())[:2]
    except (OSError, ValueError, KeyError, TypeError):
        logger.warning("Prerequisite graph unavailable", exc_info=True)
        return ()
    from app.services.content_catalog import find_path
    stages = {stage.number: stage for stage in SPINE}
    if question is not None:
        words = {word.removesuffix("s") for word in re.findall(r"[a-z]+", question.lower())}
        needs_review = bool(words & {"stuck", "confused", "review", "prerequisite", "before", "earlier", "foundation"})
        requirements = tuple(n for n in requirements if needs_review or
                             words & {word.removesuffix("s") for word in
                                      re.findall(r"[a-z]+", stages[n].title.lower())
                                      if word not in {"and", "or", "the"}})
    ids = (f"{language}-path-{n:02d}-{stages[n].slug}" for n in requirements)
    return tuple(content_id for content_id in ids if find_path(content_id))
