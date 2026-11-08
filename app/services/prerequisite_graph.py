"""Pilot prerequisite hints for focused language tutoring.

The graph guides explanations; it never grants or blocks mastery. Missing or
invalid graph data fails closed, leaving the existing RAG answer path intact.
"""
import json
import logging
import re
from functools import lru_cache
from pathlib import Path

from app.services.learning_path import SPINE, node_for_exercise

logger = logging.getLogger(__name__)
GRAPH_PATH = Path(__file__).resolve().parents[2] / "data/curriculum/prerequisite-pilot.json"


@lru_cache(maxsize=1)
def graph() -> dict[int, tuple[int, ...]]:
    raw = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    if raw.get("version") != 1 or raw.get("status") != "pilot-learning-metadata":
        raise ValueError("unsupported prerequisite graph")
    stages = {stage.number: stage for stage in SPINE}
    result: dict[int, tuple[int, ...]] = {}
    for node in raw["nodes"]:
        number = node["stage"]
        requirements = node["requires"]
        if (not isinstance(number, int) or number not in stages or number in result
                or node["slug"] != stages[number].slug or not isinstance(requirements, list)
                or len(requirements) != len(set(requirements))
                or any(not isinstance(r, int) or r >= number or r not in stages for r in requirements)):
            raise ValueError("invalid prerequisite graph node")
        result[number] = tuple(requirements)
    return result


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
