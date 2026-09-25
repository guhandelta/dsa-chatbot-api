# Analyzes a user's submitted code for a DSA problem and returns structured
# feedback (mistakes, enhancements, edge cases, interview tips).
#
# Retrieval change: for analysis we want the WHOLE reference document for the
# problem (description + optimal solution in the right language), not a few
# similarity chunks. We read it directly from the catalog by exact id, and
# only fall back to vector search if the problem isn't in the knowledge base.
import asyncio

from app.models.schemas import AnalysisResult
from app.services.knowledge_base import get_vectorstore
from app.services.llm_router import get_llm
from app.services.problem_catalog import read_problem_doc


async def _reference_context(problem_id: str) -> str:
    doc = read_problem_doc(problem_id)
    if doc:
        return doc
    # Fallback: problem not in the curated set — pull whatever is closest.
    vectorstore = get_vectorstore()
    docs = await asyncio.to_thread(vectorstore.similarity_search, problem_id, 3)
    joined = "\n\n".join(d.page_content for d in docs)
    return joined or "(No reference material found — analyze the code on its own merits.)"


def _format_execution(execution: dict | None) -> str:
    """Turn real test results into prompt evidence, so the reviewer reports
    what the code DID rather than guessing what it might do."""
    if not execution:
        return (
            "No automated test run is available for this problem. Reason about "
            "correctness from the code itself, and do NOT claim it was tested."
        )
    lines = []
    for r in execution.get("results", []):
        if r["tier"] == 1:
            lines.append(
                f"- {r['language']}: {r['status']} "
                f"({r['passed_cases']}/{r['total_cases']} test cases passed)"
                + (f" — {r['detail']}" if r["detail"] else "")
            )
    body = "\n".join(lines) or "(no executable results)"
    return (
        "The submission was ACTUALLY EXECUTED against the problem's verified "
        "test cases. These are real results, not estimates:\n" + body +
        "\n\nGround your feedback in these results. If a case failed, explain "
        "precisely why that input breaks this code. If everything passed, say "
        "so plainly and focus on complexity and style rather than inventing bugs."
    )


async def analyze_solution(
    problem_id: str,
    user_code: str,
    language: str,
    provider: str,
    execution: dict | None = None,
    evidence_summary: str | None = None,
) -> AnalysisResult:
    llm = get_llm(provider)
    reference_context = await _reference_context(problem_id)

    analysis_prompt = f"""You are a senior software engineer and DSA interview coach.

Problem: {problem_id}
Programming Language: {language}

Reference material (problem statement, approach, and optimal solutions):
{reference_context}

User's submitted solution:
```{language}
{user_code}
```

{evidence_summary or _format_execution(execution)}

Analyze the user's solution against the reference. Be specific and quote the
user's actual code where relevant. If the solution is already correct and
optimal, say so plainly rather than inventing problems. Compare its time and
space complexity to the optimal approach."""

    structured_llm = llm.with_structured_output(AnalysisResult)
    return await structured_llm.ainvoke(analysis_prompt)
