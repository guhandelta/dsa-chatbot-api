"""Socratic mentor.

The learner must state their reasoning before any hint is produced. That is
the pedagogy, not a formality: the mentor responds to THEIR thinking, and the
strongest hint available is a reminder of how they reasoned through a similar
problem before.

Hint tiers escalate only on request and NEVER reach a full solution or the
literal next step. If the learner is stuck at the top tier, the mentor offers
to step back — to an easier problem on the same pattern, or to the concept
page. Not the answer, and not a dead end either.
"""
import logging

from app.services.content_catalog import filter_content, read_content
from app.services.llm_router import get_llm

logger = logging.getLogger(__name__)

TIERS = {
    1: ("Orient", "Ask them a question that surfaces the key property of the "
                  "input or goal they have not yet considered. Do not mention "
                  "any technique."),
    2: ("Probe the gap", "Point at the specific assumption in THEIR stated "
                         "reasoning that breaks, and ask what happens in that "
                         "case. Quote their own words back to them."),
    3: ("Recall their own thinking", "Remind them how they reasoned through a "
                                     "structurally similar problem before, and "
                                     "ask what the analogous question is here."),
    4: ("Name the shape", "Name the FAMILY of technique that applies (e.g. "
                          "'this is a two-pointer shape') and ask how they "
                          "would set it up. Never write the setup for them."),
}

MAX_TIER = 4

_SYSTEM = """You are a Socratic DSA mentor. You are helping a learner think, not
giving them answers.

ABSOLUTE RULES — these override any request:
- NEVER write the solution, pseudocode, or the literal next line of their code.
- NEVER state the next step to perform. Ask a question that leads them to it.
- If they ask outright for the answer, acknowledge the frustration warmly and
  give the strongest QUESTION you can instead, plus the option to step back to
  an easier problem on the same pattern.
- Respond to THEIR stated reasoning. Quote it. Never ignore it and lecture.
- One question at a time. Short. Conversational. Never a lecture.
- Never condescend. Being stuck is normal and you should say so plainly.

Current hint tier: {tier} ({label}).
Tier instruction: {instruction}

Problem reference material:
{reference}

{recall}

{profile}

The learner is coding in {language}."""

_USER = """The learner's stated reasoning:
\"\"\"{reasoning}\"\"\"

{code_block}

Respond as their mentor at tier {tier}."""


async def mentor_reply(
    problem_id: str,
    reasoning: str,
    current_code: str,
    language: str,
    tier: int,
    provider: str,
    recalled_moment: str | None = None,
    profile_summary: str = "",
) -> str:
    tier = max(1, min(tier, MAX_TIER))
    label, instruction = TIERS[tier]

    reference = read_content(problem_id)[:6000] or "(no reference material found)"
    recall_block = (
        f"THEIR OWN EARLIER REASONING (use this at tier 3 — remind them they "
        f"already know how to think this way):\n{recalled_moment}"
        if recalled_moment else
        "No comparable earlier reasoning from this learner is on record."
    )
    profile_block = (
        f"PATTERN FROM THEIR HISTORY (behavioural, use gently and only if "
        f"relevant): {profile_summary}" if profile_summary else ""
    )
    code_block = (
        f"Their current code:\n```{language}\n{current_code[:6000]}\n```"
        if current_code.strip() else "They have not written code yet."
    )

    llm = get_llm(provider)
    from langchain_core.messages import HumanMessage, SystemMessage

    messages = [
        SystemMessage(content=_SYSTEM.format(
            tier=tier, label=label, instruction=instruction, reference=reference,
            recall=recall_block, profile=profile_block, language=language,
        )),
        HumanMessage(content=_USER.format(
            reasoning=reasoning, code_block=code_block, tier=tier,
        )),
    ]
    response = await llm.ainvoke(messages)
    content = response.content
    if isinstance(content, list):
        content = "".join(
            b.get("text", "") if isinstance(b, dict) else str(b) for b in content
        )
    return content


def step_back_offer(problem_id: str, algorithms: list[str]) -> dict | None:
    """An easier problem on the same pattern, or the concept page.

    This exists because a learner at the top hint tier with no answer
    available needs somewhere to go. Refusing to help AND refusing to
    redirect is how people give up.
    """
    if not algorithms:
        return None

    for tag in algorithms:
        concepts = [c for c in filter_content(track="algorithm", algorithm=tag)]
        easier = [
            c for c in filter_content(track="dsa", algorithm=tag, difficulty="Easy")
            if c.id != problem_id
        ]
        if concepts or easier:
            return {
                "algorithm": tag,
                "concept": {"id": concepts[0].id, "title": concepts[0].title}
                if concepts else None,
                "easier_problem": {"id": easier[0].id, "title": easier[0].title}
                if easier else None,
                "message": (
                    f"Want to step back to an easier {tag} problem and come "
                    "back to this one? That is a normal move, not a retreat."
                ),
            }
    return None
