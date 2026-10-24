"""Shared metadata contract for learning-path assessments.

The JSON banks predate this contract, so ``normalize_item`` supplies stable
defaults for legacy records. New authored records should provide the fields
explicitly; ``validate_item`` keeps both forms honest.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

ASSESSMENT_TYPES = ("mcq", "mcq_code", "short_answer", "explain", "fix_bug", "write_snippet")
ROLES = ("recognize", "trace", "explain", "debug", "implement")
DIFFICULTIES = ("easy", "medium", "hard")

_ROLE_BY_TYPE = {
    "mcq": "recognize",
    "mcq_code": "trace",
    "short_answer": "trace",
    "explain": "explain",
    "fix_bug": "debug",
    "write_snippet": "implement",
}


@dataclass(frozen=True)
class AssessmentSpec:
    id: str
    language: str
    node: str
    assessment_type: str
    role: str
    concept: str
    difficulty: str
    runtime_required: bool
    hidden_test_required: bool
    source: str


def _difficulty(item: dict[str, Any]) -> str:
    value = str(item.get("difficulty", "")).lower()
    if value in DIFFICULTIES:
        return value
    level = str(item.get("level", "L1"))
    return "hard" if level == "L4" else "medium" if level == "L3" else "easy"


def normalize_item(item: dict[str, Any], *, language: str | None = None) -> dict[str, Any]:
    """Return an item with the canonical assessment metadata populated."""
    kind = item.get("assessment_type", item.get("type"))
    role = item.get("role", _ROLE_BY_TYPE.get(kind))
    code = kind in ("mcq_code", "fix_bug", "write_snippet")
    runtime = item.get("runtime_required", code or kind == "short_answer")
    hidden = item.get("hidden_test_required", kind in ("fix_bug", "write_snippet"))
    return {
        **item,
        "language": item.get("language", language),
        "assessment_type": kind,
        "role": role,
        "skill": item.get("skill", item.get("concept", "general")),
        "difficulty": _difficulty(item),
        "runtime_required": bool(runtime),
        "hidden_test_required": bool(hidden),
    }


def validate_item(item: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ("id", "language", "node", "assessment_type", "role", "skill", "difficulty")
    for field in required:
        if not str(item.get(field, "")).strip():
            errors.append(f"missing {field}")
    if item.get("assessment_type") not in ASSESSMENT_TYPES:
        errors.append(f"unknown assessment_type {item.get('assessment_type')!r}")
    if item.get("role") not in ROLES:
        errors.append(f"unknown role {item.get('role')!r}")
    expected_role = _ROLE_BY_TYPE.get(item.get("assessment_type"))
    if expected_role and item.get("role") != expected_role:
        errors.append(f"role {item.get('role')!r} does not match {item.get('assessment_type')!r}")
    if item.get("difficulty") not in DIFFICULTIES:
        errors.append(f"unknown difficulty {item.get('difficulty')!r}")
    if item.get("runtime_required") and item.get("assessment_type") in ("mcq", "explain"):
        errors.append("runtime_required is inconsistent with assessment type")
    if item.get("hidden_test_required") and item.get("assessment_type") not in ("fix_bug", "write_snippet"):
        errors.append("hidden_test_required requires a coding assessment")
    return errors


def spec(item: dict[str, Any], *, language: str | None = None) -> AssessmentSpec:
    normalized = normalize_item(item, language=language)
    errors = validate_item(normalized)
    if errors:
        raise ValueError(f"{normalized.get('id', '<unknown>')}: {'; '.join(errors)}")
    return AssessmentSpec(
        id=normalized["id"], language=normalized["language"], node=normalized["node"],
        assessment_type=normalized["assessment_type"], role=normalized["role"],
        concept=normalized["skill"], difficulty=normalized["difficulty"],
        runtime_required=normalized["runtime_required"],
        hidden_test_required=normalized["hidden_test_required"], source=normalized.get("source", "authored"),
    )
