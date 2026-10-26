"""Learning strikes: mistakes are cleared by answering related questions.

Product rules (Guha, 2026-10-26):

* Only a failed *paid* evaluation earns a strike; free test runs never do.
* A strike records where the mistake happened, and is cleared by its own set
  of 2 or 3 questions (multiple choice, coding or debugging, in any mix)
  about the same topic. They are drawn from the quiz bank, never the problem
  that earned the strike, and the count and mix follow the learner's record.
* Solving the original problem does not clear a strike.
* Baseball rule: a wrong answer to a clearing question earns another strike,
  up to `learning_strike_cap`. What happens at the cap is not decided yet;
  `learning_strike_cap_action` is the hook.
* Reference solutions stay hidden, including for coding questions here.
* Learners may ask for extra practice on a topic at any time, strikes or not,
  within a monthly cap. It is recorded for mastery; how it counts toward
  mastery is still being framed, so the path formula does not use it yet.
"""
from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import ChallengeAnswer, ChallengeSet, LearningStrike, QuizAnswer, User

# The quiz bank's item types, grouped into the three formats learners see.
FORMATS = {"mcq": ("mcq", "mcq_code"), "coding": ("write_snippet",), "debug": ("fix_bug",)}
FORMAT_OF = {t: name for name, types in FORMATS.items() for t in types}
CODE_TYPES = FORMATS["coding"] + FORMATS["debug"]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def topic_node(language: str, problem_id: str) -> str:
    """The learning-path node a problem belongs to: the stage whose graded
    exercise it is, or whose practice set lists it."""
    from app.services.learning_path import SPINE, node_for_exercise, stage_node_id
    found = node_for_exercise(problem_id)
    if found:
        return stage_node_id(found[0], found[1])
    stage = next((s for s in SPINE if problem_id in s.problems), None)
    return stage_node_id(language, stage) if stage else ""


def _problem_tags(problem_id: str) -> set[str]:
    from app.services.content_catalog import filter_content
    item = next((c for c in filter_content() if c.id == problem_id), None)
    return set(item.algorithms) if item else set()


def candidates(language: str, node_id: str, problem_id: str) -> list[dict]:
    """Bank items on this topic in the three formats. Falls back to items
    whose concept matches the problem's algorithm tags."""
    from app.services import quiz
    pool = [i for i in quiz.pool(language, node_id) if i["type"] in FORMAT_OF] if node_id else []
    if not pool:
        tags = _problem_tags(problem_id)
        pool = [i for i in quiz.items(language).values() if i["type"] in FORMAT_OF and i.get("concept") in tags]
    return pool


async def _seen(session: AsyncSession, user_id: str) -> set[str]:
    return set((await session.scalars(select(ChallengeAnswer.item_id).where(ChallengeAnswer.user_id == user_id))).all())


async def accuracy(session: AsyncSession, user_id: str, concepts: set[str]) -> tuple[int, float]:
    """(answers, share correct) across quiz and challenge answers on these concepts."""
    if not concepts:
        return 0, 1.0
    rows = []
    for model in (QuizAnswer, ChallengeAnswer):
        rows += (await session.execute(select(model.correct).where(
            model.user_id == user_id, model.concept.in_(concepts)))).scalars().all()
    return len(rows), (sum(rows) / len(rows) if rows else 1.0)


def _format_order(where: dict) -> list[str]:
    """Lead with the format closest to the mistake."""
    phase = where.get("phase")
    if phase in ("compile", "run", "timeout") or where.get("format") == "debug":
        return ["debug", "mcq", "coding"]
    if where.get("format") == "mcq":
        return ["coding", "mcq", "debug"]
    return ["coding", "mcq", "debug"]


def pick(pool: list[dict], count: int, order: list[str], exclude: set[str], seed: str) -> list[dict]:
    """`count` items rotating through the formats in `order`. Questions the
    learner has not seen come first in every format; seen ones only fill gaps."""
    rng = random.Random(seed)
    chosen: list[dict] = []
    for fresh in (True, False):
        buckets: dict[str, list[dict]] = {name: [] for name in FORMATS}
        for item in pool:
            if (item["id"] not in exclude) == fresh and item not in chosen:
                buckets[FORMAT_OF[item["type"]]].append(item)
        for bucket in buckets.values():
            rng.shuffle(bucket)
        while len(chosen) < count and any(buckets.values()):
            for name in order:
                if buckets[name] and len(chosen) < count:
                    chosen.append(buckets[name].pop(0))
    return chosen


async def _required(session: AsyncSession, user_id: str, language: str, node_id: str, pool: list[dict]) -> int:
    """3 questions when the learner is struggling on this topic, else 2."""
    open_here = await session.scalar(select(func.count()).select_from(LearningStrike).where(
        LearningStrike.user_id == user_id, LearningStrike.language == language,
        LearningStrike.node_id == node_id, LearningStrike.status == "open"))
    answers, share = await accuracy(session, user_id, {i["concept"] for i in pool})
    struggling = (open_here or 0) >= 2 or (answers >= 3 and share < 0.6)
    return 3 if struggling else 2


async def _new_set(session, user_id, language, node_id, problem_id, kind, count, where, avoid=()):
    pool = candidates(language, node_id, problem_id)
    seen = await _seen(session, user_id) | set(avoid)
    chosen = pick(pool, count, _format_order(where), seen, seed=f"{user_id}:{node_id}:{_now().isoformat()}")
    item_set = ChallengeSet(user_id=user_id, language=language, node_id=node_id, problem_id=problem_id,
                            kind=kind, items_json=json.dumps([i["id"] for i in chosen]),
                            required=min(count, len(chosen)) if kind == "strike" else len(chosen))
    session.add(item_set)
    await session.flush()
    return item_set


async def open_count(session: AsyncSession, user_id: str, language: str, node_id: str, problem_id: str) -> int:
    topic = LearningStrike.node_id == node_id if node_id else LearningStrike.problem_id == problem_id
    return int(await session.scalar(select(func.count()).select_from(LearningStrike).where(
        LearningStrike.user_id == user_id, LearningStrike.language == language,
        LearningStrike.status == "open", topic)) or 0)


async def add_strike(session, user_id, language, problem_id, node_id, source, where) -> LearningStrike | None:
    """A new strike with its own clearing set, unless the topic is at the cap."""
    from app.services.user_lock import lock_user
    await lock_user(session, user_id)
    # Recheck under the lock: evaluation requests can finish simultaneously.
    if await open_count(session, user_id, language, node_id, problem_id) >= settings.learning_strike_cap:
        return None
    pool = candidates(language, node_id, problem_id)
    count = await _required(session, user_id, language, node_id, pool)
    # Questions already waiting in another open set are used only if nothing else is left.
    pending = (await session.scalars(select(ChallengeSet.items_json).where(
        ChallengeSet.user_id == user_id, ChallengeSet.language == language,
        ChallengeSet.completed_at.is_(None)))).all()
    waiting = {item for raw in pending for item in json.loads(raw)}
    item_set = await _new_set(session, user_id, language, node_id, problem_id, "strike", count, where, waiting)
    strike = LearningStrike(user_id=user_id, language=language, problem_id=problem_id, node_id=node_id,
                            source=source, where_json=json.dumps(where), set_id=item_set.id)
    session.add(strike)
    await session.flush()
    return strike


def evaluation_where(evidence: dict, language: str, category: str) -> dict:
    """Where a failed evaluation went wrong, from learner-safe evidence."""
    results = ((evidence or {}).get("curated") or {}).get("results") or []
    result = next((r for r in results if r.get("language") == language and r.get("tier") == 1), {})
    observed = result.get("evidence") or {}
    passed, total = result.get("passed_cases", 0), result.get("total_cases", 0)
    crashed = result.get("status") == "failed" and not passed and not result.get("case_results")
    detail = (result.get("detail") or "").lower()
    phase = observed.get("phase") or ("timeout" if "timed out" in detail else "run" if crashed
                                      else "wrong_answer" if total else "review")
    return {"stage": "evaluation", "format": "coding", "phase": phase, "category": category,
            "passed": passed, "total": total, "line": observed.get("line")}


async def record_failed_evaluation(session, user_id, problem_id, language, evidence, category):
    node_id = topic_node(language, problem_id)
    return await add_strike(session, user_id, language, problem_id, node_id, "evaluation",
                            evaluation_where(evidence, language, category))


# ---------------------------------------------------------------- views

def _items(language: str) -> dict[str, dict]:
    from app.services import quiz
    return quiz.items(language)


def _public(language: str, item_id: str) -> dict | None:
    from app.services import quiz
    item = _items(language).get(item_id)
    if item is None:
        return None
    return {**quiz.public(item), "format": FORMAT_OF.get(item["type"], "mcq")}


async def set_view(session: AsyncSession, item_set: ChallengeSet) -> dict:
    answers = {a.item_id: a for a in (await session.scalars(select(ChallengeAnswer).where(
        ChallengeAnswer.set_id == item_set.id))).all()}
    questions = []
    for item_id in json.loads(item_set.items_json):
        view = _public(item_set.language, item_id)
        if view is None:
            continue
        done = answers.get(item_id)
        view["answered"] = done is not None
        view["correct"] = bool(done and done.correct)
        questions.append(view)
    return {"id": item_set.id, "kind": item_set.kind, "node_id": item_set.node_id,
            "problem_id": item_set.problem_id, "required": item_set.required, "correct": item_set.correct,
            "answered": item_set.answered, "complete": item_set.completed_at is not None,
            "questions": questions}


async def strike_view(session: AsyncSession, strike: LearningStrike) -> dict:
    item_set = await session.get(ChallengeSet, strike.set_id) if strike.set_id else None
    return {"id": strike.id, "problem_id": strike.problem_id, "node_id": strike.node_id,
            "source": strike.source, "status": strike.status, "where": json.loads(strike.where_json),
            "created_at": strike.created_at.isoformat(),
            "set": await set_view(session, item_set) if item_set else None,
            # A topic with no authored questions cannot be cleared, so it never blocks.
            "clearable": bool(item_set and item_set.required)}


def _month_start() -> datetime:
    now = _now()
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


async def extra_remaining(session: AsyncSession, user_id: str) -> int:
    used = await session.scalar(select(func.count()).select_from(ChallengeSet).where(
        ChallengeSet.user_id == user_id, ChallengeSet.kind == "extra",
        ChallengeSet.created_at >= _month_start()))
    return max(0, settings.extra_practice_sets_per_month - int(used or 0))


async def overview(session: AsyncSession, user: User, language: str) -> dict:
    strikes = (await session.scalars(select(LearningStrike).where(
        LearningStrike.user_id == user.id, LearningStrike.language == language,
        LearningStrike.status == "open").order_by(LearningStrike.created_at))).all()
    extra = (await session.execute(select(func.count(), func.sum(ChallengeSet.correct), func.sum(ChallengeSet.answered))
                                   .where(ChallengeSet.user_id == user.id, ChallengeSet.language == language,
                                          ChallengeSet.kind == "extra"))).one()
    views = [await strike_view(session, s) for s in strikes]
    return {"language": language, "cap": settings.learning_strike_cap,
            "cap_action": settings.learning_strike_cap_action,
            "open": views, "blocking": settings.learning_strikes_gate_progress and any(v["clearable"] for v in views),
            "extra_practice": {"remaining_this_month": await extra_remaining(session, user.id),
                               "per_month": settings.extra_practice_sets_per_month,
                               "sets": int(extra[0] or 0), "correct": int(extra[1] or 0),
                               "answered": int(extra[2] or 0)}}


# ---------------------------------------------------------------- gating

async def blocking_strikes(session: AsyncSession, user_id: str, language: str) -> list[LearningStrike]:
    strikes = (await session.scalars(select(LearningStrike).where(
        LearningStrike.user_id == user_id, LearningStrike.language == language,
        LearningStrike.status == "open"))).all()
    out = []
    for strike in strikes:
        item_set = await session.get(ChallengeSet, strike.set_id) if strike.set_id else None
        if item_set and item_set.required:
            out.append(strike)
    return out


async def require_no_blocking(session: AsyncSession, user_id: str, language: str, problem_id: str) -> None:
    """Starting a different problem waits until open strikes are cleared.
    Retrying the problem that earned them is always allowed."""
    if not settings.learning_strikes_gate_progress:
        return
    strikes = await blocking_strikes(session, user_id, language)
    if any(s.problem_id != problem_id for s in strikes):
        raise HTTPException(409, {"message": "Clear your open strikes before starting a new challenge.",
                                  "open_strikes": len(strikes)})


async def blocked_nodes(session: AsyncSession, user_id: str, language: str) -> set[str]:
    return {s.node_id for s in await blocking_strikes(session, user_id, language) if s.node_id}


# ---------------------------------------------------------------- answering

async def _budget(session: AsyncSession, user_id: str, item_type: str) -> None:
    since = _now() - timedelta(hours=1)
    statement = select(func.count()).select_from(ChallengeAnswer).where(
        ChallengeAnswer.user_id == user_id, ChallengeAnswer.created_at >= since)
    if await session.scalar(statement) >= settings.quiz_answers_per_hour:
        raise HTTPException(429, "You've answered the hourly maximum of questions. Try again shortly.")
    if item_type in CODE_TYPES and await session.scalar(statement.where(
            ChallengeAnswer.item_type.in_(CODE_TYPES))) >= settings.quiz_code_runs_per_hour:
        raise HTTPException(429, "You've run the hourly maximum of coding questions. Try again shortly.")


async def owned_set(session: AsyncSession, user: User, set_id: str) -> ChallengeSet:
    item_set = await session.get(ChallengeSet, set_id)
    if item_set is None or item_set.user_id != user.id:
        raise HTTPException(404, "Challenge not found")
    return item_set


def _step_back(language: str, node_id: str) -> dict:
    """The cap hook's default: point at the previous path node and the mentor."""
    from app.services.learning_path import nodes
    path = nodes(language)
    index = next((i for i, n in enumerate(path) if n["id"] == node_id), None)
    previous = path[index - 1] if index else None
    return {"action": settings.learning_strike_cap_action,
            "message": "You've reached the strike limit on this topic. Revisit the earlier lesson or ask "
                       "the mentor for a hint before answering more.",
            "prerequisite": {"id": previous["id"], "title": previous["title"]} if previous else None}


async def answer(session: AsyncSession, user: User, set_id: str, item_id: str, response) -> dict:
    from app.services import quiz
    from app.services.user_lock import lock_user
    await lock_user(session, user.id)
    item_set = await owned_set(session, user, set_id)
    await session.refresh(item_set)
    if item_set.kind == "strike":
        await require_cap_unlocked(session, user.id, item_set)
    if await session.scalar(select(ChallengeAnswer.id).where(ChallengeAnswer.set_id == set_id, ChallengeAnswer.item_id == item_id)):
        raise HTTPException(409, "You already answered this question.")
    if item_set.completed_at is not None:
        raise HTTPException(409, "This challenge is already complete.")
    if item_id not in json.loads(item_set.items_json):
        raise HTTPException(404, "That question is not part of this challenge.")
    item = _items(item_set.language).get(item_id)
    if item is None:
        raise HTTPException(410, "This question was retired.")
    if len(str(response)) > quiz.MAX_RESPONSE:
        raise HTTPException(422, "Answers must be at most 20000 characters.")
    await _budget(session, user.id, item["type"])
    if item["type"] in CODE_TYPES:
        from app.services.code_screener import explain, screen
        from app.services.strikes import record_event
        verdict = screen(str(response), item["language"])
        if not verdict.allowed:
            outcome = await record_event(session, user, verdict, str(response), context="challenge")
            await session.commit()
            raise HTTPException(403 if outcome.get("suspended") else 400, explain(verdict) + " " + outcome.get("message", ""))
    result = await quiz.grade(item, response)
    try:
        async with session.begin_nested():
            session.add(ChallengeAnswer(set_id=set_id, user_id=user.id, item_id=item_id, item_type=item["type"],
                                        concept=item.get("concept", ""), response=str(response),
                                        correct=result["correct"], score=result["score"]))
            await session.flush()
    except IntegrityError:
        raise HTTPException(409, "You already answered this question.")
    item_set.answered += 1
    item_set.correct += int(result["correct"])
    outcome: dict = {"new_strike": None, "replacement": None, "cap_reached": None, "cleared": False,
                     "renewed_set": None}

    if item_set.kind == "strike":
        strike = await session.scalar(select(LearningStrike).where(LearningStrike.set_id == set_id))
        if result["correct"] and item_set.correct >= item_set.required:
            item_set.completed_at = _now()
            if strike:
                strike.status, strike.cleared_at = "cleared", _now()
            outcome["cleared"] = True
        elif not result["correct"]:
            # The missed question is replaced so the set can still be cleared.
            used = set(json.loads(item_set.items_json))
            pool = candidates(item_set.language, item_set.node_id, item_set.problem_id)
            fresh = pick([i for i in pool if i["id"] not in used], 1, _format_order({"format": FORMAT_OF[item["type"]]}),
                         await _seen(session, user.id), seed=f"{set_id}:{item_set.answered}")
            if fresh:
                item_set.items_json = json.dumps([*used_in_order(item_set), fresh[0]["id"]])
                outcome["replacement"] = _public(item_set.language, fresh[0]["id"])
            else:
                done = await _answered(session, set_id)
                remaining = sum(1 for q in used if q not in done)
                if strike and item_set.correct + remaining < item_set.required:
                    # The topic's questions are used up in this set, so it could
                    # never be cleared. Start the strike on a new set instead.
                    item_set.completed_at = _now()
                    renewed = await _new_set(session, user.id, item_set.language, item_set.node_id,
                                             item_set.problem_id, "strike", item_set.required,
                                             {"format": FORMAT_OF[item["type"]]})
                    strike.set_id = renewed.id
                    outcome["renewed_set"] = await set_view(session, renewed)
            where = {"stage": "challenge", "format": FORMAT_OF[item["type"]], "item_id": item_id,
                     "concept": item.get("concept", ""), "from_strike": strike.id if strike else None}
            added = await add_strike(session, user.id, item_set.language, item_set.problem_id,
                                     item_set.node_id, "challenge", where)
            if added:
                outcome["new_strike"] = await strike_view(session, added)
            else:
                outcome["cap_reached"] = _step_back(item_set.language, item_set.node_id)
    elif item_set.answered >= len(json.loads(item_set.items_json)):
        item_set.completed_at = _now()
    await session.commit()
    if item["type"] in CODE_TYPES:
        # Reference solutions stay hidden, including for clearing questions.
        result.pop("expected", None)
    return {**result, **outcome, "item_id": item_id, "set": await set_view(session, item_set)}


def used_in_order(item_set: ChallengeSet) -> list[str]:
    return json.loads(item_set.items_json)


async def _answered(session: AsyncSession, set_id: str) -> set[str]:
    return set((await session.scalars(select(ChallengeAnswer.item_id).where(ChallengeAnswer.set_id == set_id))).all())


async def start_extra(session: AsyncSession, user: User, language: str, problem_id: str = "",
                      node_id: str = "", count: int = 3) -> dict:
    from app.services.user_lock import lock_user
    await lock_user(session, user.id)
    if await extra_remaining(session, user.id) <= 0:
        raise HTTPException(429, f"You've used this month's {settings.extra_practice_sets_per_month} extra "
                                 "practice sets. They reset on the 1st.")
    node_id = node_id or (topic_node(language, problem_id) if problem_id else "")
    if not candidates(language, node_id, problem_id):
        raise HTTPException(409, "There are no practice questions for this topic yet.")
    item_set = await _new_set(session, user.id, language, node_id, problem_id, "extra", count, {"format": "coding"})
    await session.commit()
    return await set_view(session, item_set)


async def export_for_user(session: AsyncSession, user_id: str) -> dict:
    strikes = (await session.scalars(select(LearningStrike).where(LearningStrike.user_id == user_id)
                                     .order_by(LearningStrike.created_at))).all()
    answers = (await session.scalars(select(ChallengeAnswer).where(ChallengeAnswer.user_id == user_id)
                                     .order_by(ChallengeAnswer.created_at))).all()
    return {"strikes": [{"problem_id": s.problem_id, "language": s.language, "source": s.source,
                         "where": json.loads(s.where_json), "status": s.status,
                         "created_at": s.created_at.isoformat(),
                         "cleared_at": s.cleared_at.isoformat() if s.cleared_at else None} for s in strikes],
            "challenge_answers": [{"item_id": a.item_id, "type": a.item_type, "concept": a.concept,
                                   "response": a.response, "correct": a.correct,
                                   "created_at": a.created_at.isoformat()} for a in answers]}


async def require_cap_unlocked(session, user_id, item_set):
    """In lock mode, a completed mentor hint after reaching the cap is required."""
    if settings.learning_strike_cap_action != "lock":
        return
    if await open_count(session, user_id, item_set.language, item_set.node_id, item_set.problem_id) < settings.learning_strike_cap:
        return
    latest = await session.scalar(select(func.max(LearningStrike.created_at)).where(
        LearningStrike.user_id == user_id, LearningStrike.language == item_set.language,
        LearningStrike.status == "open",
        LearningStrike.node_id == item_set.node_id if item_set.node_id else LearningStrike.problem_id == item_set.problem_id))
    from app.db.models import LearningEvent
    hints = (await session.scalars(select(LearningEvent).where(
        LearningEvent.user_id == user_id, LearningEvent.language == item_set.language,
        LearningEvent.kind == "hint", LearningEvent.created_at > latest))).all()
    if not any(h.problem_id == item_set.problem_id or (item_set.node_id and topic_node(item_set.language, h.problem_id) == item_set.node_id) for h in hints):
        raise HTTPException(409, "Strike limit reached. Ask the mentor for a hint on this topic before answering more clearing questions.")


async def delete_for_user(session, user_id):
    from sqlalchemy import delete
    for model in (LearningStrike, ChallengeAnswer, ChallengeSet):
        await session.execute(delete(model).where(model.user_id == user_id))
