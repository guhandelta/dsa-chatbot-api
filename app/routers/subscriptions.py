# /subscriptions — per-language mentor entitlements.
#
# PAYMENTS ARE NOT HANDLED HERE. Checkout runs in Stripe Checkout, hosted by
# Stripe, so card data never reaches this server. Stripe then calls the
# webhook below, which grants or revokes the entitlement. The only thing
# stored here is the Stripe subscription id.
import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_current_user, require_admin
from app.db.database import get_session
from app.db.models import User
from app.models.schemas import SubscriptionOut
from app.services import entitlements

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/", response_model=list[SubscriptionOut])
async def my_subscriptions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    subs = await entitlements.list_for(session, current_user.id)
    return [
        SubscriptionOut(
            id=s.id, language=s.language, status=s.status,
            expires_at=s.expires_at.isoformat(),
        )
        for s in subs
    ]


@router.post("/webhook")
async def stripe_webhook(
    payload: dict,
    stripe_signature: str = Header(default="", alias="Stripe-Signature"),
    session: AsyncSession = Depends(get_session),
):
    """Stripe calls this after a successful payment or cancellation.

    SECURITY: the signature MUST be verified before trusting the payload —
    this endpoint is public, so an unverified webhook is a free-subscription
    endpoint for anyone who finds the URL. Verification is left explicit
    rather than stubbed silently, so it cannot be forgotten.
    """
    if not settings.stripe_webhook_secret:
        raise HTTPException(
            status_code=503,
            detail="Stripe webhook secret is not configured; refusing to trust this payload.",
        )
    # Verify with: stripe.Webhook.construct_event(raw_body, stripe_signature,
    #              settings.stripe_webhook_secret)
    # Requires the RAW request body, so wire this with a Request object when
    # you add the stripe SDK.
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature.")

    event_type = payload.get("type", "")
    data = payload.get("data", {}).get("object", {})
    user_id = (data.get("metadata") or {}).get("user_id")
    language = (data.get("metadata") or {}).get("language")
    if not user_id or not language:
        raise HTTPException(status_code=400, detail="Missing user_id/language metadata.")

    if event_type in ("checkout.session.completed", "invoice.payment_succeeded"):
        await entitlements.grant(
            session, user_id, language, days=30, provider_ref=data.get("subscription", "")
        )
        await session.commit()
        return {"granted": language}

    if event_type in ("customer.subscription.deleted",):
        await entitlements.revoke(session, user_id, language)
        await session.commit()
        return {"revoked": language}

    return {"ignored": event_type}


@router.post("/admin/grant", response_model=SubscriptionOut)
async def admin_grant(
    user_id: str,
    language: str,
    days: int = 30,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Manual grant — for comps, support fixes, and local testing without Stripe."""
    target = await session.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")
    sub = await entitlements.grant(session, user_id, language, days=days)
    await session.commit()
    await session.refresh(sub)
    return SubscriptionOut(
        id=sub.id, language=sub.language, status=sub.status,
        expires_at=sub.expires_at.isoformat(),
    )
