# /subscriptions — per-language mentor entitlements.
#
# PAYMENTS ARE NOT HANDLED HERE. Checkout runs in Stripe Checkout, hosted by
# Stripe, so card data never reaches this server. Stripe then calls the
# webhook below, which grants or revokes the entitlement. The only thing
# stored here is the Stripe subscription id.
import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Query
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
async def stripe_webhook(request: Request,
    stripe_signature: str = Header(default="",alias="Stripe-Signature"),
    session: AsyncSession = Depends(get_session)):
    import hashlib
    from datetime import datetime, timezone
    from sqlalchemy.exc import IntegrityError
    from app.db.models import Subscription, WebhookReceipt
    from app.services.webhooks import verified_event
    raw=await request.body()
    if len(raw)>1_000_000:raise HTTPException(413,'Webhook payload too large.')
    event=verified_event(raw,stripe_signature,settings.stripe_webhook_secret)
    digest=hashlib.sha256(raw).hexdigest()
    existing=await session.get(WebhookReceipt,event['id'])
    if existing:
        if existing.payload_hash!=digest:raise HTTPException(409,'Event ID was reused with different data.')
        return {'duplicate':True}
    session.add(WebhookReceipt(id=event['id'],payload_hash=digest))
    try:await session.flush()
    except IntegrityError:
        await session.rollback()
        existing=await session.get(WebhookReceipt,event['id'])
        if existing is None or existing.payload_hash!=digest:raise HTTPException(409,'Event ID conflict.')
        return {'duplicate':True}
    kind=event.get('type','')
    data=event.get('data',{}).get('object',{})
    # Entitlement periods come from signed subscription state, not guessed
    # 30-day additions. Checkout/invoice pricing rules remain deferred.
    if kind not in ('customer.subscription.created','customer.subscription.updated','customer.subscription.deleted'):
        await session.commit()
        return {'ignored':kind}
    ref=data.get('id')
    if not isinstance(ref,str) or not ref:raise HTTPException(400,'Missing subscription ID.')
    sub=await session.scalar(select(Subscription).where(Subscription.provider_ref==ref))
    metadata=data.get('metadata') or {}
    uid=metadata.get('user_id') or (sub.user_id if sub else None)
    language=metadata.get('language') or (sub.language if sub else None)
    if not uid or not language or await session.get(User,uid) is None:raise HTTPException(400,'Unknown subscription owner or language.')
    if sub and (sub.user_id!=uid or sub.language!=language):raise HTTPException(409,'Subscription ownership cannot change through a webhook.')
    period=data.get('current_period_end')
    if period is None:
        period=max((i.get('current_period_end',0) for i in (data.get('items') or {}).get('data',[])),default=0)
    if not isinstance(period,(int,float)) or period<=0:raise HTTPException(400,'Missing subscription period.')
    expires=datetime.fromtimestamp(period,timezone.utc)
    status=data.get('status')
    # Only signed active/trialing state creates access. Cancellation retains
    # the reported period; unpaid, expired, or incomplete state cannot grant.
    state = ('cancelled' if kind=='customer.subscription.deleted' else
             'inactive' if status not in ('active','trialing') else
             'cancelled' if data.get('cancel_at_period_end') else 'active')
    event_time=event.get('created',0)
    if not isinstance(event_time,int) or event_time<0:raise HTTPException(400,'Invalid event timestamp.')
    if sub is None and kind=='customer.subscription.deleted':
        await session.commit()
        return {'ignored':'unknown cancelled subscription'}
    if sub is None:
        sub=Subscription(user_id=uid,language=language,provider_ref=ref,expires_at=expires,status=state,provider_event_timestamp=event_time)
        session.add(sub)
    else:
        # Delayed updates must not roll a renewed period backwards.
        current=sub.expires_at.replace(tzinfo=timezone.utc) if sub.expires_at.tzinfo is None else sub.expires_at
        if expires>=current and event_time>=sub.provider_event_timestamp:
            sub.expires_at=expires;sub.status=state;sub.provider_event_timestamp=event_time
    await session.commit()
    return {'updated':language}


@router.post("/admin/grant", response_model=SubscriptionOut)
async def admin_grant(
    user_id: str,
    language: str = Query(min_length=1,max_length=20),
    days: int = Query(default=30,ge=1,le=3650),
    issuer: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
    idempotency_key: str | None = Header(default=None),
):
    from app.services.operations import perform
    if await session.get(User,user_id) is None:
        raise HTTPException(404,"User not found")
    async def work(_):
        sub=await entitlements.grant(session,user_id,language,days=days)
        await session.flush()
        return SubscriptionOut(id=sub.id,language=sub.language,status=sub.status,
                               expires_at=sub.expires_at.isoformat())
    return await perform(session,issuer.id,'subscription:grant',idempotency_key,
                         {'user_id':user_id,'language':language,'days':days},0,'admin-grant',work)
