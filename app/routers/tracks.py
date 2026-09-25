# /tracks — the three learning paths, each with Learn and Practice.
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.db.models import User
from app.services.content_catalog import (
    ContentMeta,
    filter_content,
    known_algorithms,
    known_languages,
    read_content,
    track_summary,
)

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.get("/")
def list_tracks(current_user: User = Depends(get_current_user)):
    """Track-selection screen: the three paths, their counts, and the
    learner's saved language."""
    return {
        "tracks": track_summary(),
        "languages": known_languages(),
        "preferred_language": current_user.preferred_language,
        "modes": ["learn", "practice"],
    }


@router.get("/{track}/items", response_model=list[ContentMeta])
def track_items(
    track: str,
    difficulty: str | None = None,
    algorithm: str | None = None,
    source: str | None = None,
    language: str | None = None,
    current_user: User = Depends(get_current_user),
):
    """Content within a track, filtered. The language track is filtered by the
    learner's preferred language unless overridden."""
    if track not in ("language", "dsa", "algorithm"):
        raise HTTPException(status_code=404, detail="Unknown track")
    lang = language or (current_user.preferred_language if track == "language" else None)
    return filter_content(
        track=track, language=lang, difficulty=difficulty,
        algorithm=algorithm, source=source,
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
