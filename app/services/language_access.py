"""Role and language access shared by every learning entry point.

Instructor assignments are administered explicitly. A saved, non-rejected
reference upload also establishes its author's language scope. Training remains
available to both author roles, including their first upload in a new language.
"""
import json
from datetime import timezone

from fastapi import HTTPException
from sqlalchemy import select

from app.db.models import InstructorLanguage, KnowledgeDocument, Submission, Subscription


def available_languages():
    from app.services.content_catalog import known_languages
    from app.services.reference_library import subjects
    return sorted(set(known_languages()) | {s['language'] for s in subjects()}
                  | {'javascript', 'java'})


async def allowed_languages(session, user):
    if user.status != 'active':
        return []
    available = set(available_languages())
    if user.role == 'admin':
        return sorted(available)
    if user.role == 'instructor':
        languages = set((await session.scalars(select(InstructorLanguage.language).where(
            InstructorLanguage.user_id == user.id))).all())
        from app.services.uploaded_knowledge import infer_language
        uploads = (await session.execute(select(KnowledgeDocument.filename, KnowledgeDocument.language).where(
            KnowledgeDocument.owner_id == user.id,
            KnowledgeDocument.status.in_(('pending', 'published'))))).all()
        languages.update(language or infer_language(filename) for filename, language in uploads)
        # Only languages supplied by the author count, not generated solutions.
        submissions = (await session.scalars(select(Submission.raw_input).where(
            Submission.user_id == user.id,
            Submission.status.in_(('published', 'needs_review'))))).all()
        for raw_input in submissions:
            try:
                raw = json.loads(raw_input)
                solutions = raw.get('supplied', {})
                if isinstance(solutions, dict):
                    languages.update(k for k, v in solutions.items() if isinstance(v, str) and v.strip())
            except (ValueError, AttributeError):
                continue
        return sorted(languages & available)
    if user.role != 'student':
        return []
    from app.services.entitlements import _now
    now = _now()
    subscriptions = (await session.scalars(select(Subscription).where(
        Subscription.user_id == user.id,
        Subscription.status.in_(('active', 'cancelled'))))).all()
    return sorted({s.language for s in subscriptions
                   if (s.expires_at.replace(tzinfo=timezone.utc) if s.expires_at.tzinfo is None
                       else s.expires_at) > now} & available)


async def require_language(session, user, language):
    if user.status != 'active':
        raise HTTPException(403, 'This account is suspended.')
    if language not in await allowed_languages(session, user):
        reason = ('An active subscription covering this language is required.'
                  if user.role == 'student' else
                  'This language must be assigned for teaching or associated with your uploaded content.')
        raise HTTPException(403, reason)
    return language


async def resolve_language(session, user, language=None):
    if language:
        return await require_language(session, user, language)
    languages = await allowed_languages(session, user)
    if not languages:
        raise HTTPException(403, 'No learning languages are currently available for this account.')
    return user.preferred_language if user.preferred_language in languages else languages[0]


async def require_content(session, user, content_id, language=None):
    from app.services.content_catalog import filter_content
    item = next((c for c in filter_content() if c.id == content_id), None)
    if item is None:
        raise HTTPException(404, 'Content not found')
    if item.language and language and item.language != language:
        raise HTTPException(403, 'Choose the content language before opening this item.')
    return await resolve_language(session, user, item.language or language)


async def access_view(session, user):
    languages = await allowed_languages(session, user)
    return {'role': user.role, 'languages': languages,
            'preferred_language': user.preferred_language if user.preferred_language in languages else
                                  next(iter(languages), None),
            'can_train': user.status == 'active' and user.role in ('admin', 'instructor'),
            'available_languages': available_languages() if user.role == 'admin' else languages}
