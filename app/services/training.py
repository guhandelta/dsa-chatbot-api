"""LLM stage of the training pipeline.

Takes whatever an instructor submits (a statement, plus zero or more solutions in
any languages) and produces a complete, canonical problem:

  * corrected solutions for all six languages, with every correction recorded
  * a per-solution explanation
  * "thinking style" notes — the transferable reasoning pattern, so a learner
    can take notes and adapt the approach to unseen problems
  * executable test cases (args + expected) used by code_runner to verify

IMPORTANT: nothing here is trusted. Everything this module returns is a
*candidate*; app/services/training.py only publishes it after code_runner
actually executes it. The LLM proposes, the compiler and test suite decide.
"""
from pydantic import BaseModel, Field
from typing import Literal

from app.services.llm_router import get_llm

LANGUAGES = ["python", "javascript", "java", "cpp", "c", "rust"]

# Function names the test harness will call. Fixed per language so the
# generated code and the runner always agree.
NAME_HINT = {
    "python": "snake_case",
    "javascript": "camelCase",
    "java": "camelCase",
    "cpp": "camelCase",
    "c": "camelCase",
    "rust": "snake_case",
}


class SolutionOut(BaseModel):
    language: str = Field(description="one of: python, javascript, java, cpp, c, rust")
    function_name: str = Field(
        description="Exact name of the primary function defined in the code. "
        "The test harness calls this name, so it must match the code exactly."
    )
    code: str = Field(
        description="Complete function definition only — no imports of test "
        "frameworks, no main(), no example usage, no markdown fences. "
        "Python/JavaScript must define a top-level function callable as "
        "function_name(*args) matching the test case argument order."
    )
    explanation: str = Field(
        description="2-4 sentences explaining how this implementation works and "
        "any language-specific details (memory handling in C, ownership in Rust, etc.)"
    )
    corrections: list[str] = Field(
        default_factory=list,
        description="If the instructor supplied this language and it had bugs, list each "
        "bug found and how it was fixed. Empty if it was already correct or newly written.",
    )
    was_supplied: bool = Field(description="True if the instructor provided this language")


class TestCase(BaseModel):
    args: list = Field(
        description="Positional arguments as JSON, in the order the function takes them. "
        "e.g. for two_sum(nums, target): [[2,7,11,15], 9]"
    )
    expected: object = Field(description="Expected return value as JSON")
    note: str = Field(default="", description="What this case checks, e.g. 'empty input'")


class EnrichedProblem(BaseModel):
    """The canonical problem the LLM proposes for publication."""

    title: str = Field(description="Problem title, e.g. 'Two Sum (LC 1)'")
    difficulty: str = Field(description="Easy, Medium, or Hard")
    category: str = Field(description="Comma-separated tags, e.g. 'Array, Hash Map'")
    statement: str = Field(description="Clear problem statement in your own words")
    examples: list[str] = Field(description="2-3 worked examples as 'input → output' lines")
    constraints: list[str] = Field(default_factory=list, description="Input constraints")
    hints: list[str] = Field(description="2-4 progressive hints that guide without spoiling")
    approach: str = Field(description="The optimal approach with time and space complexity")
    thinking_style: list[str] = Field(
        description="The transferable reasoning pattern: what signals in the problem point "
        "to this technique, and what class of problems it generalises to. Written as notes "
        "a learner can study and reuse on unseen problems."
    )
    edge_cases: list[str] = Field(description="Edge cases a solver must handle")
    interview_tips: list[str] = Field(description="Common interviewer follow-ups")
    issues_found: list[str] = Field(
        default_factory=list,
        description="Problems found in what the instructor submitted: wrong statement, "
        "misstated complexity, buggy code, missing constraints. Empty if it was clean.",
    )
    solutions: list[SolutionOut] = Field(
        description="EXACTLY one entry per language: python, javascript, java, cpp, c, rust"
    )
    comparison: Literal["exact", "unordered_flat", "unordered_nested"] = Field(
        default="exact", description="Keep arrays and matrices ordered unless the statement explicitly permits reordering."
    )
    test_cases: list[TestCase] = Field(
        description="6-10 test cases including edge cases. Must be verifiably correct — "
        "these are executed against every implementation."
    )


def _prompt(problem_hint: str, supplied: dict[str, str]) -> str:
    if supplied:
        supplied_block = "\n\n".join(
            f"### {lang}\n```\n{code}\n```" for lang, code in supplied.items()
        )
    else:
        supplied_block = "(none — the instructor supplied no code)"

    return f"""You are a meticulous DSA curriculum author and code reviewer.

An instructor has submitted the following problem for the knowledge base:

--- SUBMITTED PROBLEM ---
{problem_hint}

--- SUBMITTED SOLUTIONS ---
{supplied_block}
--- END SUBMISSION ---

Your tasks:

1. REVIEW what was submitted. If the statement is ambiguous, the stated
   complexity is wrong, or any supplied code has a bug (wrong output, missed
   edge case, off-by-one, leak, overflow), record it in `issues_found` and in
   that solution's `corrections`. Do not silently fix things — always report.

2. PRODUCE a correct implementation for ALL SIX languages: python, javascript,
   java, cpp, c, rust. Fix supplied ones; write missing ones from scratch.
   Set `was_supplied` accordingly.

3. NAMING: use {NAME_HINT['python']} for python/rust and {NAME_HINT['javascript']}
   for the others. `function_name` MUST exactly match the function defined in
   `code`.

4. CRITICAL — python and javascript are EXECUTED against your test cases.
   Define a plain top-level function (no class wrapper, no I/O, no printing)
   callable as function_name(*args) where args are exactly your test case
   `args` in order. Return the value; never print it.

5. TEST CASES: 6-10 cases including edge cases (empty input, single element,
   duplicates, negatives, all-same). Compute `expected` by hand from the
   problem definition — every implementation is executed against these, so an
   incorrect expected value will wrongly fail correct code.

6. TEACHING CONTENT: write `explanation` for each solution, plus
   `thinking_style` — the reusable reasoning pattern (what clues point to this
   technique, what family of problems it unlocks), written for a learner
   taking notes.

Be rigorous. Correctness matters more than elegance."""


async def enrich_problem(problem_hint: str, supplied: dict[str, str],
                         provider: str = "openai") -> EnrichedProblem:
    """Single structured-output call returning the full candidate problem."""
    llm = get_llm(provider)
    structured = llm.with_structured_output(EnrichedProblem)
    return await structured.ainvoke(_prompt(problem_hint, supplied))


async def repair_solutions(problem: EnrichedProblem, failures: list[dict],
                           provider: str = "openai") -> EnrichedProblem:
    """Second pass: the validator rejected some implementations, so feed the
    actual compiler/test output back and ask for a targeted fix."""
    failure_block = "\n".join(
        f"- {f['language']} ({f['status']}): {f['detail']}" for f in failures
    )
    solutions_block = "\n\n".join(
        f"### {s.language} (fn: {s.function_name})\n```\n{s.code}\n```"
        for s in problem.solutions
    )
    prompt = f"""Your previous solutions for "{problem.title}" were executed and
some FAILED. Real compiler and test-runner output:

{failure_block}

Current solutions:
{solutions_block}

Test cases they were run against:
{[{"args": t.args, "expected": t.expected} for t in problem.test_cases]}

Fix the failing implementations. If a failure is caused by an INCORRECT TEST
CASE rather than incorrect code, fix the test case instead and say so in
`issues_found`. Return the complete corrected problem with all six languages."""

    llm = get_llm(provider)
    structured = llm.with_structured_output(EnrichedProblem)
    return await structured.ainvoke(prompt)


def to_markdown(p: EnrichedProblem) -> str:
    """Render the canonical knowledge-base markdown (same format the catalog
    parses and the RAG pipeline ingests)."""
    import json
    lines = ["---", "track: dsa", f"difficulty: {p.difficulty}",
             "source: authored", "io_mode: function", f"comparison: {p.comparison}"]
    for solution in p.solutions:
        lines.append(f"fn_{solution.language}: {solution.function_name}")
    lines += ["test_cases: " + json.dumps([t.model_dump() for t in p.test_cases]),
              "---", f"# {p.title} — {p.difficulty} — {p.category}", ""]
    lines += ["## Problem", p.statement, ""]
    if p.examples:
        lines += ["## Examples"] + [f"- {e}" for e in p.examples] + [""]
    if p.constraints:
        lines += ["## Constraints"] + [f"- {c}" for c in p.constraints] + [""]
    lines += ["## Approach", p.approach, ""]
    if p.hints:
        lines += ["## Hints"] + [f"{i}. {h}" for i, h in enumerate(p.hints, 1)] + [""]
    if p.thinking_style:
        lines += ["## Thinking Style (transferable pattern)"]
        lines += [f"- {t}" for t in p.thinking_style] + [""]
    if p.edge_cases:
        lines += ["## Edge Cases"] + [f"- {e}" for e in p.edge_cases] + [""]

    lines += ["## Solutions", ""]
    label = {"python": "Python", "javascript": "JavaScript", "java": "Java",
             "cpp": "C++", "c": "C", "rust": "Rust"}
    fence = {"python": "python", "javascript": "javascript", "java": "java",
             "cpp": "cpp", "c": "c", "rust": "rust"}
    order = ["python", "javascript", "java", "cpp", "c", "rust"]
    by_lang = {s.language: s for s in p.solutions}
    for lang in order:
        s = by_lang.get(lang)
        if not s:
            continue
        lines += [f"### {label[lang]}", f"```{fence[lang]}", s.code.strip(), "```", ""]
        if s.explanation:
            lines += [s.explanation, ""]
        if s.corrections:
            lines += ["*Corrections applied:*"] + [f"- {c}" for c in s.corrections] + [""]

    if p.interview_tips:
        lines += ["## Interview Follow-ups"] + [f"- {t}" for t in p.interview_tips] + [""]
    return "\n".join(lines)
