"""Orchestrates the training pipeline:

    submit -> enrich (LLM) -> validate (execute) -> repair if needed
           -> re-validate -> auto-publish only if the gate passes

Auto-publish requires: every Tier-1 implementation passes all test cases,
Tier-1 implementations agree with each other, and every Tier-2 language whose
toolchain is installed compiles. Anything short of that is saved as
`needs_review` with the full report — nothing half-verified reaches learners.
"""
import asyncio
import json
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
    return run_suite(solutions, fn_names, cases, expected)


async def run_pipeline(problem_id: str, problem_hint: str,
                       supplied: dict[str, str], provider: str = "openai") -> dict:
    """Returns {status, report, markdown, problem}. Never raises on validation
    failure — a failed run is a normal outcome that gets reported back."""
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
        Path(PROBLEMS_DIR / f"{problem_id}.md").write_text(markdown)
        list_problems.cache_clear()          # catalog picks it up immediately
        chunks = await asyncio.to_thread(upsert_problem, problem_id, markdown)
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
        "results": [
            {"language": r["language"], "status": r["status"],
             "cases": f"{r['passed_cases']}/{r['total_cases']}" if r["tier"] == 1 else "-",
             "detail": r["detail"][:200]}
            for r in report["results"]
        ],
    }


def submission_payload(problem_hint: str, supplied: dict[str, str]) -> str:
    return json.dumps({"hint": problem_hint, "supplied": supplied})
