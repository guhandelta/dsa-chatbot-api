# /tracks — the three learning paths, each with Learn and Practice.
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.db.models import User
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
def list_tracks(current_user: User = Depends(get_current_user)):
    """The section-choice screen: three sections, their counts, and the
    learner's saved language.

    Counts are scoped to the learner's language for Language Fundamentals,
    which is the only language-specific section.
    """
    return {
        "tracks": track_summary(language=current_user.preferred_language),
        "languages": known_languages(),
        "preferred_language": current_user.preferred_language,
        # `browse` opens on the topic list rather than a chat box: landing in
        # an empty conversation with no context makes the learner invent a
        # question before they have seen what is available.
        "modes": ["browse", "learn", "practice"],
    }


@router.get("/language/levels")
def language_levels(
    language: str | None = None,
    current_user: User = Depends(get_current_user),
):
    """The three progression levels of Language Fundamentals, with counts
    scoped to one language (the learner's own unless overridden)."""
    lang = language or current_user.preferred_language
    return {
        "language": lang,
        "levels": level_summary(lang),
        "valid_levels": list(LEVELS),
    }


@router.get("/patterns/tags")
def pattern_tags(_: User = Depends(get_current_user)):
    """Design-pattern tags in use anywhere in the catalog."""
    return {"patterns": known_patterns()}


@router.get("/patterns/{pattern}/related", response_model=list[ContentMeta])
def pattern_related(
    pattern: str,
    language: str | None = None,
    current_user: User = Depends(get_current_user),
):
    """Everything tagged with this pattern, across every section.

    Returns the Design Patterns page alongside any Language Fundamentals
    idiom pages that implement it — the cross-link that lets the two sections
    reference each other without either duplicating the other's content.
    """
    lang = language or current_user.preferred_language
    items = filter_content(pattern=pattern)
    return [c for c in items if c.language in (None, lang)]


@router.get("/{track}/items", response_model=list[ContentMeta])
def track_items(
    track: str,
    difficulty: str | None = None,
    algorithm: str | None = None,
    source: str | None = None,
    language: str | None = None,
    level: str | None = None,
    pattern: str | None = None,
    current_user: User = Depends(get_current_user),
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
    lang = language or (current_user.preferred_language if track == "language" else None)
    return filter_content(
        track=track, language=lang, difficulty=difficulty,
        algorithm=algorithm, source=source, level=level, pattern=pattern,
    )


@router.get("/algorithms/tags")
def algorithm_tags(_: User = Depends(get_current_user)):
    """Algorithm tags in use — powers the algorithm-track picker and links a
    concept to the problems that practise it."""
    return {"algorithms": known_algorithms()}


@router.get("/algorithms/{algorithm}/practice", response_model=list[ContentMeta])
def algorithm_practice(
    algorithm: str,
    difficulty: str | None = None,
    _: User = Depends(get_current_user),
):
    """The practice half of the algorithm track: problems tagged with this
    algorithm, optionally at one difficulty, so a learner can move Easy →
    Medium → Hard on a single technique."""
    items = [c for c in filter_content(algorithm=algorithm, difficulty=difficulty)
             if c.track == "dsa"]
    if not items:
        raise HTTPException(
            status_code=404,
            detail=f"No practice problems tagged '{algorithm}' yet. Train some first.",
        )
    return items


@router.get("/items/{content_id}")
def get_item(content_id: str, _: User = Depends(get_current_user)):
    body = read_content(content_id)
    if not body:
        raise HTTPException(status_code=404, detail="Content not found")
    return {"id": content_id, "markdown": body}
