"""Orchestrates the training pipeline:

    submit -> enrich (LLM) -> validate (execute) -> repair if needed
           -> re-validate -> auto-publish only if the gate passes

Auto-publish requires executable JavaScript and Java references, at least six
 distinct fixture inputs, and complete execution of every supplied implementation.
Compilation alone, missing runtimes, and shared failures never count as verification.
Tests establish observed correctness, not a proof of correctness for all inputs.
"""
import asyncio
import json
import os
import re
import tempfile
from pathlib import Path

from app.services import training
from app.services.code_runner import run_suite
from app.services.knowledge_base import upsert_problem
from app.services.problem_catalog import PROBLEMS_DIR, list_problems

MAX_REPAIR_ROUNDS = 1


def _validate(problem: training.EnrichedProblem) -> dict:
    solutions = {s.language: s.code for s in problem.solutions}
    fn_names = {s.language: s.function_name for s in problem.solutions}
    cases = [t.args for t in problem.test_cases]
    expected = [t.expected for t in problem.test_cases]
    issues = []
    languages = [s.language for s in problem.solutions]
    if len(languages) != len(set(languages)):
        issues.append("Duplicate solution languages are not allowed.")
    if not {"javascript", "java"}.issubset(languages):
        issues.append("DSA publication requires JavaScript and Java solutions.")
    if set(languages) - set(training.LANGUAGES):
        issues.append("Unsupported solution language.")
    try:
        unique = {json.dumps(args, sort_keys=True, allow_nan=False) for args in cases}
        json.dumps(expected, allow_nan=False)
        if len(unique) < 6:
            issues.append("At least six distinct fixture inputs are required.")
    except (TypeError, ValueError):
        issues.append("Fixtures must contain finite JSON values.")
    if any(not s.code.strip() or not re.fullmatch(r"[A-Za-z_]\w*", s.function_name)
           for s in problem.solutions):
        issues.append("Every solution needs code and a valid function name.")
    if issues:
        return {"results": [], "agreement": False, "agreement_detail": "validation blocked",
                "can_publish": False, "unverified": languages, "validation_errors": issues}
    report = run_suite(solutions, fn_names, cases, expected, comparison=problem.comparison)
    report["validation_errors"] = []
    return report


async def run_pipeline(problem_id: str, problem_hint: str,
                       supplied: dict[str, str], provider: str = "openai") -> dict:
    """Returns {status, report, markdown, problem}. Never raises on validation
    failure — a failed run is a normal outcome that gets reported back."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,119}", problem_id):
        raise ValueError("Invalid problem id")
    stages: list[dict] = []

    problem = await training.enrich_problem(problem_hint, supplied, provider)
    stages.append({"stage": "enrich", "issues_found": problem.issues_found,
                   "languages": [s.language for s in problem.solutions],
                   "test_case_count": len(problem.test_cases)})

    # Execution happens in subprocesses; keep the event loop free.
    report = await asyncio.to_thread(_validate, problem)
    stages.append({"stage": "validate", **_summary(report)})

    rounds = 0
    while not report["can_publish"] and rounds < MAX_REPAIR_ROUNDS:
        failures = [r for r in report["results"] if r["status"] == "failed"]
        if not failures:
            break  # blocked by disagreement alone; a repair pass won't help
        problem = await training.repair_solutions(problem, failures, provider)
        report = await asyncio.to_thread(_validate, problem)
        rounds += 1
        stages.append({"stage": f"repair_{rounds}", **_summary(report)})

    markdown = training.to_markdown(problem)
    status = "published" if report["can_publish"] else "needs_review"

    if status == "published":
        PROBLEMS_DIR.mkdir(parents=True, exist_ok=True)
        destination = PROBLEMS_DIR / f"{problem_id}.md"
        # Keep the learner catalog unchanged if indexing fails. Replace the
        # file atomically only after the index accepts the validated document.
        with tempfile.NamedTemporaryFile(mode="w", dir=PROBLEMS_DIR,
                                         suffix=".pending", delete=False) as draft:
            draft.write(markdown)
            pending = Path(draft.name)
        try:
            chunks = await asyncio.to_thread(upsert_problem, problem_id, markdown)
            os.replace(pending, destination)
        finally:
            pending.unlink(missing_ok=True)
        list_problems.cache_clear()
        from app.services.content_catalog import list_content
        from app.services.curriculum_search import _index
        list_content.cache_clear()
        _index.cache_clear()
        stages.append({"stage": "publish", "chunks_indexed": chunks})

    return {
        "status": status,
        "problem_id": problem_id,
        "title": problem.title,
        "issues_found": problem.issues_found,
        "corrections": {
            s.language: s.corrections for s in problem.solutions if s.corrections
        },
        "generated_languages": [s.language for s in problem.solutions if not s.was_supplied],
        "unverified_languages": report["unverified"],
        "validation": report,
        "stages": stages,
        "markdown": markdown,
    }


def _summary(report: dict) -> dict:
    return {
        "can_publish": report["can_publish"],
        "agreement": report["agreement_detail"],
        "validation_errors": report.get("validation_errors", []),
        "results": [
            {"language": r["language"], "status": r["status"],
             "cases": f"{r['passed_cases']}/{r['total_cases']}" if r["tier"] == 1 else "-",
             "detail": r["detail"][:200]}
            for r in report["results"]
        ],
    }


def submission_payload(problem_hint: str, supplied: dict[str, str]) -> str:
    return json.dumps({"hint": problem_hint, "supplied": supplied})
