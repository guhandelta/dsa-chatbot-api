"""Learning-pattern tracking.

DESIGN CONSTRAINT
-----------------
Everything recorded here is OBSERVABLE BEHAVIOUR: what the learner submitted,
which inputs it failed on, which algorithm tags were involved, how many hint
tiers they used. Nothing here infers traits, learner types, or personality.

That is a deliberate limit, not an oversight. "You have missed the empty-input
case in four problems" is accurate, actionable, and reads as help. "You are a
careless thinker" is unreliable, unfalsifiable, and demoralising — and being
told what *kind* of person you are lands very differently from being told what
you did. The first drives teaching; the second drives churn.

Error categories are derived DETERMINISTICALLY from execution evidence (the
fuzzer's minimal counterexamples), never from a model's opinion, so the
resulting profile is factual.
"""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LearningEvent, QuizAnswer, StudentPathRecord

# Human-readable category -> the transferable lesson behind it.
CATEGORY_LESSON = {
    "empty_input": "handling empty or zero-length input",
    "single_element": "handling a single-element input",
    "duplicate_values": "handling repeated values",
    "negative_values": "handling negative numbers",
    "all_negative": "the case where every value is negative",
    "boundary_index": "off-by-one at the first or last index",
    "element_reuse": "using the same element twice when the problem forbids it",
    "no_solution_case": "the case where no valid answer exists",
    "wrong_return_shape": "returning the wrong shape or type",
    "timeout": "efficiency — the solution is too slow",
    "runtime_error": "an unhandled runtime error",
    "complexity": "achieving the required time complexity",
}


def categorize_failure(evidence: dict) -> tuple[str, str]:
    """Derive an error category from execution evidence.

    Returns (category, human detail). Purely rule-based over the actual
    failing inputs — no LLM involved, so the category is as reliable as the
    execution result it came from.
    """
    fuzz = (evidence or {}).get("fuzz") or {}
    curated = (evidence or {}).get("curated") or {}

    # Runtime / timeout signals from the curated run come first
    for r in curated.get("results", []):
        detail = (r.get("detail") or "").lower()
        if "timed out" in detail:
            return "timeout", "The submission exceeded the time limit."
        if r.get("status") == "failed" and not r.get("passed_cases"):
            if "error" in detail or "traceback" in detail:
                return "runtime_error", detail[:200]

    counterexamples = fuzz.get("counterexamples") or []
    if not counterexamples:
        return "", ""

    first = counterexamples[0]
    args = first.get("args") or []
    student = first.get("student_output")
    reference = first.get("reference_output")

    lists = [a for a in args if isinstance(a, list)]
    primary = lists[0] if lists else []
    numeric = [x for x in primary if isinstance(x, (int, float))]

    # Priority order matters: the category a learner sees should be the MOST
    # informative one that applies, not whichever rule happens to run first.
    # An empty-input failure that also returns the wrong type is an
    # empty-input lesson, not a typing lesson.

    # 1. Returning the same index twice is unambiguous element reuse
    if (isinstance(student, list) and len(student) == 2
            and student[0] == student[1]
            and not (isinstance(reference, list) and len(reference) == 2
                     and reference[0] == reference[1])):
        return "element_reuse", "Uses the same element twice."

    # 2. Empty input, before any shape reasoning
    if isinstance(primary, list) and len(primary) == 0:
        return "empty_input", "Fails on empty input."

    # 3. Duplicates outrank sign/length: if values repeat, that IS the lesson
    if primary and len(set(map(str, primary))) < len(primary):
        return "duplicate_values", "Fails when values repeat."

    # 4. All-negative is more instructive than "single element" when both hold
    if numeric and len(numeric) == len(primary) and all(x < 0 for x in numeric):
        return "all_negative", "Fails when every value is negative."

    if isinstance(primary, list) and len(primary) == 1:
        return "single_element", "Fails on a single-element input."

    if any(x < 0 for x in numeric):
        return "negative_values", "Fails when negative values are present."

    # 4. Shape mismatch only once the input-shape lessons are ruled out
    if type(student) is not type(reference) and not (
        isinstance(student, (int, float)) and isinstance(reference, (int, float))
    ):
        return "wrong_return_shape", (
            f"Returned {type(student).__name__} where {type(reference).__name__} was expected."
        )

    if reference in ([], -1, None) and student not in ([], -1, None):
        return "no_solution_case", "Returns an answer where none exists."

    if isinstance(primary, list) and len(primary) <= 2:
        return "boundary_index", "Fails at a boundary index."

    return "logic", first.get("description", "")[:200]


@dataclass
class LearningProfile:
    total_attempts: int = 0
    solved: int = 0
    recurring_errors: list[tuple[str, int]] = field(default_factory=list)
    weak_algorithms: list[tuple[str, int]] = field(default_factory=list)
    strong_algorithms: list[tuple[str, int]] = field(default_factory=list)
    avg_hint_tier: float = 0.0
    languages: list[str] = field(default_factory=list)

    def summary(self) -> str:
        """Learner-facing text. Describes behaviour and names the lesson —
        never characterises the person."""
        if not self.total_attempts:
            return "Not enough activity yet to spot patterns."
        bits: list[str] = []
        if self.recurring_errors:
            top = self.recurring_errors[0]
            lesson = CATEGORY_LESSON.get(top[0], top[0].replace("_", " "))
            bits.append(
                f"{lesson.capitalize()} has tripped you up in {top[1]} submissions"
            )
        if self.weak_algorithms:
            names = ", ".join(a for a, _ in self.weak_algorithms[:2])
            bits.append(f"most of your failed attempts involve {names}")
        if self.strong_algorithms:
            names = ", ".join(a for a, _ in self.strong_algorithms[:2])
            bits.append(f"you solve {names} problems reliably")
        if not bits:
            return "No clear pattern yet."
        joined = bits[0] + "".join("; " + b for b in bits[1:])
        return joined + "."

    def to_dict(self) -> dict:
        return {
            "total_attempts": self.total_attempts,
            "solved": self.solved,
            "recurring_errors": [
                {"category": c, "count": n,
                 "lesson": CATEGORY_LESSON.get(c, c.replace("_", " "))}
                for c, n in self.recurring_errors
            ],
            "weak_algorithms": [{"algorithm": a, "failures": n} for a, n in self.weak_algorithms],
            "strong_algorithms": [{"algorithm": a, "solves": n} for a, n in self.strong_algorithms],
            "avg_hint_tier": round(self.avg_hint_tier, 2),
            "languages": self.languages,
            "summary": self.summary(),
        }


async def record_event(
    session: AsyncSession, user_id: str, problem_id: str, kind: str,
    language: str = "python", algorithms: list[str] | None = None,
    error_category: str = "", detail: str = "", hint_tier: int = 0,
    reasoning: str = "", billing_operation_id: str | None = None,
    expected_generation: int | None = None,
    practice_session_id: str | None = None,
) -> None:
    if expected_generation is not None:
        from sqlalchemy import update
        from app.db.models import User
        # Hold the erasure lock through the event/receipt commit. An old hint
        # may finish, but must not restore reasoning erased while it ran.
        await session.execute(update(User).where(User.id == user_id).values(peppercorns=User.peppercorns))
        generation = await session.scalar(select(User.profile_generation).where(User.id == user_id))
        if generation != expected_generation:
            return
    event = LearningEvent(
        user_id=user_id, problem_id=problem_id, kind=kind, language=language,
        practice_session_id=practice_session_id,
        algorithms=",".join(algorithms or []), error_category=error_category,
        detail=detail[:1000], hint_tier=hint_tier, reasoning=reasoning[:2000],
    )
    session.add(event)
    if kind == "hint":
        from app.db.models import HintUsage
        await session.flush()
        usage = await session.scalar(select(HintUsage).where(
            HintUsage.operation_id == billing_operation_id)) if billing_operation_id else None
        if usage is not None:
            usage.event_id = event.id
        else:
            session.add(HintUsage(user_id=user_id, problem_id=problem_id, language=language,
                                  tier=hint_tier, event_id=event.id, created_at=event.created_at))


async def _events(session: AsyncSession, user_id: str, limit: int = 500) -> list[LearningEvent]:
    stmt = (select(LearningEvent)
            .where(LearningEvent.user_id == user_id)
            .order_by(LearningEvent.created_at.desc())
            .limit(limit))
    return list((await session.execute(stmt)).scalars())


async def build_profile(session: AsyncSession, user_id: str) -> LearningProfile:
    events = await _events(session, user_id)
    profile = LearningProfile()
    if not events:
        return profile

    errors: Counter = Counter()
    fail_algos: Counter = Counter()
    solve_algos: Counter = Counter()
    hint_tiers: list[int] = []
    languages: set[str] = set()

    for e in events:
        languages.add(e.language)
        algos = [a for a in e.algorithms.split(",") if a]
        if e.kind == "attempt":
            profile.total_attempts += 1
            if e.error_category:
                errors[e.error_category] += 1
                for a in algos:
                    fail_algos[a] += 1
        elif e.kind == "solved":
            profile.solved += 1
            for a in algos:
                solve_algos[a] += 1
        elif e.kind == "hint":
            hint_tiers.append(e.hint_tier)

    # Only surface a pattern once it has actually recurred. A single failure
    # is noise, and presenting it as a "pattern" is both wrong and discouraging.
    profile.recurring_errors = [(c, n) for c, n in errors.most_common(5) if n >= 2]
    profile.weak_algorithms = [(a, n) for a, n in fail_algos.most_common(5) if n >= 2]
    profile.strong_algorithms = [
        (a, n) for a, n in solve_algos.most_common(5)
        if n >= 2 and fail_algos.get(a, 0) < n
    ]
    profile.avg_hint_tier = sum(hint_tiers) / len(hint_tiers) if hint_tiers else 0.0
    profile.languages = sorted(languages)
    return profile


async def recall_similar_moment(
    session: AsyncSession, user_id: str, algorithms: list[str], problem_id: str, language: str | None = None,
) -> str | None:
    """Find a moment where this learner reasoned their way through a related
    problem, so the mentor can remind them of their OWN thinking.

    This is the heart of the hint strategy: not "here is the technique", but
    "you worked this out before — what was the question you asked yourself?"
    """
    if not algorithms:
        return None
    stmt = select(LearningEvent).where(LearningEvent.user_id == user_id)
    if language is not None:
        stmt = stmt.where(LearningEvent.language == language)
    events = list((await session.scalars(stmt.order_by(LearningEvent.created_at.desc()).limit(300))).all())
    tags = set(algorithms)

    for e in events:
        if e.problem_id == problem_id or not e.reasoning:
            continue
        if e.kind not in ("solved", "hint", "reflection"):
            continue
        if tags & {a for a in e.algorithms.split(",") if a}:
            if e.kind in ("reflection", "solved"):
                solved = await session.scalar(select(LearningEvent.id).where(
                    LearningEvent.user_id == user_id, LearningEvent.problem_id == e.problem_id,
                    LearningEvent.language == e.language, LearningEvent.kind == "solved",
                    LearningEvent.created_at <= e.created_at).limit(1))
                if solved is None:
                    continue
                provenance = "reasoning associated with a verified solve; the wording itself is not proof"
            else:
                provenance = "unfinished hint reasoning; no verified success is implied"
            return (f'On "{e.problem_id}" ({e.language}) you wrote: "{e.reasoning[:300]}" — '
                    + provenance + ".")
    return None


async def export_profile(session: AsyncSession, user_id: str) -> dict:
    """Full export of everything stored about this learner. A behavioural
    profile of a paying customer must be exportable and deletable on request."""
    events = list((await session.scalars(select(LearningEvent).where(
        LearningEvent.user_id == user_id).order_by(LearningEvent.created_at.desc()))).all())
    profile = await build_profile(session, user_id)
    return {
        "profile": profile.to_dict(),
        "events": [
            {
                "problem_id": e.problem_id, "kind": e.kind, "language": e.language,
                "algorithms": e.algorithms, "error_category": e.error_category,
                "hint_tier": e.hint_tier, "reasoning": e.reasoning,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ],
        "student_path_records": [
            {"id": record.id, "section": record.section, "language": record.language,
             "kind": record.kind, "concept_id": record.concept_id or None,
             "body": record.body, "curriculum_version": record.curriculum_version,
             "created_at": record.created_at.isoformat()}
            for record in (await session.scalars(select(StudentPathRecord).where(
                StudentPathRecord.user_id == user_id).order_by(
                StudentPathRecord.created_at.desc(), StudentPathRecord.id.desc()))).all()
        ],
        # Study Room quiz answers, including the learner's typed explanations.
        "quiz_answers": [
            {
                "item_id": a.item_id, "type": a.item_type, "concept": a.concept,
                "response": a.response, "correct": a.correct, "score": a.score,
                "feedback": a.feedback, "misconception": a.misconception,
                "understanding": json.loads(a.understanding_json) if a.understanding_json else None,
                "created_at": a.created_at.isoformat(),
            }
            for a in (await session.scalars(select(QuizAnswer).where(
                QuizAnswer.user_id == user_id).order_by(QuizAnswer.created_at.desc()))).all()
        ],
        # Practice workspace files, snapshots and test-run history.
        "workspace": await _workspace_export(session, user_id),
        # Learning strikes and the answers given to clear them.
        "strikes": await _strikes_export(session, user_id),
    }


async def _strikes_export(session: AsyncSession, user_id: str) -> dict:
    from app.services.learning_strikes import export_for_user
    return await export_for_user(session, user_id)


async def _workspace_export(session: AsyncSession, user_id: str) -> dict:
    from app.services import workspace
    return await workspace.export_for_user(session, user_id)


async def delete_profile(session: AsyncSession, user_id: str) -> int:
    """Erase the profile, workspace files and challenges; preserve billing facts."""
    from sqlalchemy import update
    from app.db.models import User
    from app.services.hint_billing import preserve_legacy
    await session.execute(update(User).where(User.id == user_id).values(profile_generation=User.profile_generation + 1))
    await preserve_legacy(session, user_id)
    result = await session.execute(delete(LearningEvent).where(LearningEvent.user_id == user_id))
    await session.execute(delete(StudentPathRecord).where(StudentPathRecord.user_id == user_id))
    from app.services.quiz import delete_for_user
    await delete_for_user(session, user_id)
    from app.services import workspace, learning_strikes
    await workspace.delete_for_user(session, user_id)
    await learning_strikes.delete_for_user(session, user_id)
    return result.rowcount
