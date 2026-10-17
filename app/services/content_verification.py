"""Executable reference checks shared by learner preflight and the offline audit.

Cached by source bytes and runtime availability. Editing an exercise invalidates
its result. A passing suite is evidence for those cases, never a universal proof.
"""
import hashlib
import json
from functools import lru_cache

from app.services import content_catalog as catalog
from app.services.code_runner import available_languages, run_suite


def fixture_errors(cases: list, expected: list) -> list[str]:
    errors = []
    if len(cases) != len(expected):
        errors.append("Input and expected-output counts differ.")
    try:
        unique = {json.dumps(c, sort_keys=True, allow_nan=False) for c in cases}
        json.dumps(expected, allow_nan=False)
        if len(unique) < 6:
            errors.append("At least six distinct test inputs are required.")
        if any(not isinstance(c, list) for c in cases):
            errors.append("Function arguments must be JSON arrays.")
    except (ValueError, TypeError):
        errors.append("Fixtures must contain finite JSON values.")
    return errors


def verify_reference(content_id: str, language: str) -> dict:
    path = catalog.find_path(content_id)
    if not path:
        return {"verified": False, "issues": ["This is reference material, not an executable exercise."]}
    raw = path.read_text()
    runtime = bool(available_languages().get(language))
    # Digest plus path prevents stale results after edits or catalog redirection.
    from app.core.config import settings
    return _verify(content_id, language, str(path), raw, runtime,
                   settings.exec_backend, settings.exec_container_image)


@lru_cache(maxsize=512)
def _verify(content_id: str, language: str, path: str, raw: str, runtime: bool, backend: str, image: str) -> dict:
    digest = hashlib.sha256(raw.encode()).hexdigest()
    try:
        cases, expected, fns, io_mode = catalog.load_test_cases(content_id, text=raw)
        reference = catalog.reference_solution(content_id, language, text=raw)
    except (KeyError, TypeError, ValueError) as exc:
        return {"verified": False, "source_sha256": digest,
                "issues": [f"Malformed exercise fixtures: {type(exc).__name__}"]}
    issues = fixture_errors(cases, expected)
    if not reference:
        issues.append(f"No executable {language} reference solution.")
    if not runtime:
        issues.append(f"The {language} runtime is unavailable.")
    if issues:
        return {"verified": False, "source_sha256": digest, "issues": issues}
    code, fn = reference
    report = run_suite({language: code}, {**fns, language: fn}, cases, expected, io_mode,
                       comparison=catalog.comparison_mode(content_id, text=raw))
    return {"verified": report["can_publish"], "source_sha256": digest,
            "case_count": len(cases), "issues": [] if report["can_publish"] else
            [r["detail"] for r in report["results"] if r["status"] != "passed"],
            "execution": report}


async def require_verified_reference(content_id: str, language: str) -> None:
    """Fail before charging or recording learner progress on invalid fixtures."""
    import asyncio
    from fastapi import HTTPException
    if language not in ('java', 'javascript'):
        return  # Existing additional-language reviews are not certified by this gate.
    result = await asyncio.to_thread(verify_reference, content_id, language)
    if not result['verified']:
        raise HTTPException(422, 'This exercise is awaiting verified tests and a passing '
                            f'{language} reference solution. Choose another exercise.')
