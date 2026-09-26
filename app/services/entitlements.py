"""Per-language mentor subscriptions.

A subscription is scoped to ONE programming language. A Python subscriber gets
Socratic mentoring whenever they are coding in Python — across all three
tracks, since the mentor responds to the language you are writing in.

Peppercorns are unaffected: the subscription UNLOCKS the mentor, and each
mentor turn still costs peppercorns. Two gates, two purposes — the
subscription is access, peppercorns are usage.

PAYMENTS: this module never sees card data. Checkout happens in Stripe
Checkout (hosted by Stripe), and a webhook calls `grant` / `revoke` with the
Stripe subscription id. That keeps card data entirely off this server.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Subscription


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def active_for(session: AsyncSession, user_id: str, language: str) -> Subscription | None:
    stmt = select(Subscription).where(
        Subscription.user_id == user_id,
        Subscription.language == language,
        Subscription.status == "active",
    )
    for sub in (await session.execute(stmt)).scalars():
        expires = sub.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires > _now():
            return sub
    return None


async def check(session: AsyncSession, user_id: str, language: str) -> dict:
    """Returns an entitlement decision with a reason the UI can show verbatim."""
    sub = await active_for(session, user_id, language)
    if sub:
        expires = sub.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return {
            "language": language,
            "entitled": True,
            "reason": f"Active {language} mentor subscription.",
            "expires_at": expires.isoformat(),
        }
    return {
        "language": language,
        "entitled": False,
        "reason": (
            f"Mentor guidance for {language} requires a {language} subscription. "
            "Reviews, chat, and practice remain available without one."
        ),
        "expires_at": None,
    }


async def list_for(session: AsyncSession, user_id: str) -> list[Subscription]:
    stmt = select(Subscription).where(Subscription.user_id == user_id)
    return list((await session.execute(stmt)).scalars())


async def grant(session: AsyncSession, user_id: str, language: str,
                days: int = 30, provider_ref: str = "") -> Subscription:
    """Called by the Stripe webhook on successful payment, or by an admin.

    Extends an existing active subscription rather than stacking a second one,
    so a renewal adds time instead of creating a duplicate entitlement.
    """
    existing = await active_for(session, user_id, language)
    if existing:
        expires = existing.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        existing.expires_at = expires + timedelta(days=days)
        if provider_ref:
            existing.provider_ref = provider_ref
        session.add(existing)
        return existing

    sub = Subscription(
        user_id=user_id, language=language, status="active",
        expires_at=_now() + timedelta(days=days), provider_ref=provider_ref,
    )
    session.add(sub)
    return sub


async def revoke(session: AsyncSession, user_id: str, language: str) -> bool:
    """Cancellation. The entitlement runs to the end of the paid period —
    cancelling should not confiscate time already paid for."""
    sub = await active_for(session, user_id, language)
    if not sub:
        return False
    sub.status = "cancelled"
    session.add(sub)
    return True
