# /tracks — the three learning paths, each with Learn and Practice.
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.db.models import User
from app.services.language_access import allowed_languages, available_languages, resolve_language, require_language, require_content
from app.db.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.content_catalog import (
    LEVELS,
    SECTIONS,
    ContentMeta,
    filter_content,
    known_algorithms,
    known_languages,
    known_patterns,
    level_summary,
    read_content,
    track_summary,
)

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.get("/")
async def list_tracks(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """The section-choice screen: three sections, their counts, and the
    learner's saved language.

    Counts are scoped to the learner's language for Language Fundamentals,
    which is the only language-specific section.
    """
    languages = await allowed_languages(session, current_user)
    language = current_user.preferred_language if current_user.preferred_language in languages else next(iter(languages), None)
    return {
        "tracks": [t for t in track_summary(language=language)
                   if language and t["track"] in ("language", "dsa")],
        "languages": languages,
        "training_languages": available_languages() if current_user.role in ('admin', 'instructor') else [],
        "preferred_language": language,
        # `browse` opens on the topic list rather than a chat box: landing in
        # an empty conversation with no context makes the learner invent a
        # question before they have seen what is available.
        "modes": ["browse", "learn", "practice"],
    }


@router.get("/language/levels")
async def language_levels(
    language: str | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """The three progression levels of Language Fundamentals, with counts
    scoped to one language (the learner's own unless overridden)."""
    lang = await resolve_language(session, current_user, language)
    return {
        "language": lang,
        "levels": level_summary(lang),
        "valid_levels": list(LEVELS),
    }


@router.get("/language/progress")
async def language_progress(
    language: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    from sqlalchemy import select
    from app.db.models import LearningEvent
    await require_language(session, current_user, language)
    ids = list((await session.scalars(select(LearningEvent.problem_id).where(
        LearningEvent.user_id == current_user.id,
        LearningEvent.language == language,
        LearningEvent.kind == "solved",
    ).distinct())).all())
    lessons = sorted([c for c in filter_content(track="language", language=language)
                      if 0 < c.order < 100], key=lambda c: c.order)
    completed = [c.id for c in lessons if c.id in ids]
    return {"completed_ids": completed, "total": len(lessons),
            "next_id": next((c.id for c in lessons if c.id not in completed), None)}


@router.get("/patterns/tags")
def pattern_tags(_: User = Depends(get_current_user)):
    """Design-pattern tags in use anywhere in the catalog."""
    return {"patterns": known_patterns()}


@router.get("/patterns/{pattern}/related", response_model=list[ContentMeta])
async def pattern_related(
    pattern: str,
    language: str | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Everything tagged with this pattern, across every section.

    Returns the Design Patterns page alongside any Language Fundamentals
    idiom pages that implement it — the cross-link that lets the two sections
    reference each other without either duplicating the other's content.
    """
    lang = await resolve_language(session, current_user, language)
    items = filter_content(pattern=pattern)
    return [c for c in items if c.language in (None, lang)]


@router.get("/reference-subjects")
async def reference_subjects(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """Imported knowledge for reference chat; no new executable workouts implied."""
    from app.services.reference_library import subjects
    allowed = await allowed_languages(session, user)
    return {"subjects": [s for s in subjects() if s["language"] in allowed], "retrieval": "local_bm25", "status": "reference_only"}


@router.get("/{track}/items", response_model=list[ContentMeta])
async def track_items(
    track: str,
    difficulty: str | None = None,
    algorithm: str | None = None,
    source: str | None = None,
    language: str | None = None,
    level: str | None = None,
    pattern: str | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Content within a section, filtered. Language Fundamentals is scoped to
    the learner's preferred language unless overridden.

    Accepts a section name ("dsa") or an internal track name ("algorithm").
    """
    if track not in SECTIONS and track != "algorithm":
        raise HTTPException(
            status_code=404,
            detail=f"Unknown section '{track}'. Valid: {', '.join(SECTIONS)}",
        )
    if level and level not in LEVELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown level '{level}'. Valid: {', '.join(LEVELS)}",
        )
    lang = await resolve_language(session, current_user, language)
    return sorted(filter_content(
        track=track, language=lang, difficulty=difficulty,
        algorithm=algorithm, source=source, level=level, pattern=pattern,
    ), key=lambda c: (c.order or 999, c.title))


@router.get("/algorithms/tags")
def algorithm_tags(_: User = Depends(get_current_user)):
    """Algorithm tags in use — powers the algorithm-track picker and links a
    concept to the problems that practise it."""
    return {"algorithms": known_algorithms()}


@router.get("/algorithms/{algorithm}/practice", response_model=list[ContentMeta])
async def algorithm_practice(
    algorithm: str,
    difficulty: str | None = None,
    user: User = Depends(get_current_user),
    language: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """The practice half of the algorithm track: problems tagged with this
    algorithm, optionally at one difficulty, so a learner can move Easy →
    Medium → Hard on a single technique."""
    lang = await resolve_language(session, user, language)
    items = [c for c in filter_content(algorithm=algorithm, difficulty=difficulty, language=lang)
             if c.track == "dsa"]
    if not items:
        raise HTTPException(
            status_code=404,
            detail=f"No practice problems tagged '{algorithm}' yet. Train some first.",
        )
    return items


@router.get("/items/{content_id}")
async def get_item(content_id: str, language: str | None = None, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await require_content(session, user, content_id, language)
    body = read_content(content_id)
    if not body:
        raise HTTPException(status_code=404, detail="Content not found")
    from app.services.content_access import learner_document
    return {"id": content_id, "markdown": learner_document(content_id)}
