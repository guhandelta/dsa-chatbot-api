"""Learner-safe execution evidence.

Curated test cases are hidden content (content_access.public_text strips
them from the problem). The runners, however, describe a wrong answer as
"case 3: got 7, expected 12" and keep the program's raw outputs, which is what
instructors need when validating a reference solution. Before evidence
reaches a learner, a model prompt, or anything stored with the learner's
session, it goes through `learner_safe`:

* raw outputs are replaced by one pass/fail flag per case;
* a wrong-answer detail becomes "N/M test cases passed";
* any other runner "case N: got ..., expected ..." fragment is masked.

Compiler and runtime messages about the learner's own code are kept, because
they are the diagnostics the learner needs. Fuzz counterexamples are generated
inputs, not hidden tests, and stay as they are.
"""
from __future__ import annotations

import copy
import re

# The runners' wrong-answer wording: "case 3: got 7, expected 12" (several
# cases are joined with "; "). Learner error messages are left alone.
_CASE_FRAGMENT = re.compile(r"case (\d+): got .*?, expected .*?(?=; case \d+:|$)", re.S)


def mask(text: str) -> str:
    return _CASE_FRAGMENT.sub(lambda m: f"case {m.group(1)}: wrong answer", text or "")


def _case_flags(outputs: list, expected: list, mode: str) -> list[bool]:
    from app.services.output_comparison import compare
    return [i < len(outputs) and bool(compare(outputs[i], want, mode)) for i, want in enumerate(expected)]


def learner_safe(evidence: dict | None, problem_id: str) -> dict | None:
    """A copy of `evidence` with hidden test values removed. Idempotent."""
    if not evidence:
        return evidence
    safe = copy.deepcopy(evidence)
    curated = safe.get("curated") or {}
    if curated.get("results"):
        from app.services.content_catalog import comparison_mode, load_test_cases
        _, expected, _, _ = load_test_cases(problem_id)
        mode = comparison_mode(problem_id)
        for result in curated["results"]:
            outputs = result.pop("outputs", None) or []
            if outputs and "case_results" not in result:
                result["case_results"] = _case_flags(outputs, expected, mode)
            wrong_answer = result.get("status") == "failed" and (outputs or result.get("passed_cases"))
            if wrong_answer:
                result["detail"] = f"{result.get('passed_cases', 0)}/{result.get('total_cases', 0)} test cases passed"
            else:
                result["detail"] = mask(result.get("detail", ""))
            if isinstance(result.get("evidence"), dict) and result["evidence"].get("message"):
                result["evidence"]["message"] = mask(result["evidence"]["message"])
            result.setdefault("outputs", [])
    return safe
