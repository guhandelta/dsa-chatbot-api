"""Suggested reading order for the existing Design Patterns reference lessons."""
import json
from functools import lru_cache
from pathlib import Path

from app.services.content_catalog import ContentMeta

PATH = Path(__file__).resolve().parents[2] / "data/curriculum/design-patterns-reference.json"


@lru_cache(maxsize=1)
def sequence() -> dict[str, tuple[int, list[str]]]:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    if data.get("version") != 1 or data.get("status") != "suggested-reference-order-not-graded":
        raise ValueError("unsupported pattern reference path")
    ordered: dict[str, tuple[int, list[str]]] = {}
    for index, row in enumerate(data["items"], 1):
        content_id = row["id"]
        requires = row["requires"]
        if content_id in ordered or not isinstance(requires, list) or any(r not in ordered for r in requires):
            raise ValueError("invalid pattern reference path")
        ordered[content_id] = (index, requires)
    return ordered


def arrange(items: list[ContentMeta]) -> list[ContentMeta]:
    order = sequence()
    sorted_items = sorted(items, key=lambda item: (order.get(item.id, (999, []))[0], item.title))
    return [item.model_copy(update={"order": index,
                                    "prerequisites": order.get(item.id, (999, []))[1]})
            for index, item in enumerate(sorted_items, 1)]
