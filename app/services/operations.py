"""One durable debit/result per authenticated idempotency key.

A retry of a completed request replays the receipt. In-flight duplicates and
key/body mismatches fail without running work. Failure rolls back feature
writes and refunds the committed reservation in one terminal transaction.
"""
import asyncio
import hashlib
import json
import logging
import uuid
from datetime import datetime,timedelta,timezone

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update

from app.db.models import ServiceOperation, User
from app.services.peppercorns import debit, credit, InsufficientPeppercornsError

logger = logging.getLogger(__name__)


def operation_id(user_id, scope, key):
    return hashlib.sha256(json.dumps([user_id, scope, key]).encode()).hexdigest()


async def perform(session, user_id, scope, key, payload, amount, reason, work, *, prepare=None):
    if key is not None and (not key.strip() or len(key)>128):
        raise HTTPException(422,"Idempotency-Key must contain 1–128 characters.")
    # Legacy clients without a key remain supported. The UI always sends one.
    key = key or str(uuid.uuid4())
    op_id=operation_id(user_id,scope,key)
    fingerprint=hashlib.sha256(json.dumps(jsonable_encoder(payload),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    existing=await session.get(ServiceOperation,op_id)
    if existing:
        if existing.fingerprint!=fingerprint:
            raise HTTPException(409,"This idempotency key was already used with different input.")
        if existing.state=='running':
            created=existing.created_at.replace(tzinfo=timezone.utc) if existing.created_at.tzinfo is None else existing.created_at
            if created < datetime.now(timezone.utc)-timedelta(minutes=30):
                detail='The earlier request expired before completion. Its reservation was refunded; start a new request.'
                changed=await session.execute(update(ServiceOperation).where(ServiceOperation.id==op_id,ServiceOperation.state=='running').values(state='failed',http_status=503,response_json=json.dumps({'detail':detail})))
                if changed.rowcount:
                    if existing.amount:await credit(session,user_id,existing.amount,'refund:'+existing.reason)
                    if scope.startswith('practice:') and scope!='practice:start':
                        from app.db.models import PracticeSession
                        await session.execute(update(PracticeSession).where(PracticeSession.id==scope[len('practice:'):],PracticeSession.user_id==user_id,PracticeSession.busy_token==op_id).values(busy=False,busy_token=""))
                    await session.commit()
                raise HTTPException(503,detail)
            raise HTTPException(409,"This request is still processing. Retry with the same key.",headers={"Retry-After":"2"})
        body=json.loads(existing.response_json)
        if existing.http_status>=400:
            raise HTTPException(existing.http_status,body.get('detail','Request failed.'))
        return body
    op=ServiceOperation(id=op_id,user_id=user_id,scope=scope,fingerprint=fingerprint,amount=0,reason=reason)
    session.add(op)
    try:
        await session.flush()
        await session.commit()  # preserve the claim even when preflight later rolls back
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409,"This request is already processing. Retry with the same key.",headers={"Retry-After":"2"})
    try:
        # Serialize per-user preflight/rate-limit/debit decisions on both
        # supported databases, closing the count-before-debit race.
        await session.execute(update(User).where(User.id==user_id).values(peppercorns=User.peppercorns))
        status=await session.scalar(select(User.status).where(User.id==user_id))
        if status!='active':raise HTTPException(403,'This account is suspended.')
        if prepare:
            await prepare()
        balance=await debit(session,user_id,amount,reason) if amount else None
        op.amount=amount
        await session.commit()  # receipt and debit become durable together
        response=await work(balance)
        body=jsonable_encoder(response)
        changed=await session.execute(update(ServiceOperation).where(ServiceOperation.id==op_id,ServiceOperation.state=='running').values(state='completed',response_json=json.dumps(body),http_status=200))
        if not changed.rowcount:
            raise RuntimeError('Operation has already been settled')
        await session.commit()  # feature writes + receipt are atomic
        return body
    except BaseException as error:
        await session.rollback()
        # A rejected preflight can include a committed security event. No debit
        # exists yet. Persist a receipt so transport retries do not add strikes.
        status=error.status_code if isinstance(error,HTTPException) else 402 if isinstance(error,InsufficientPeppercornsError) else 502
        detail=error.detail if isinstance(error,HTTPException) else str(error) if isinstance(error,InsufficientPeppercornsError) else 'The service could not complete this request. Any reserved peppercorns were refunded.'
        async def settle():
            # Only the worker that wins this transition may issue the refund.
            # The recorded amount, not an in-memory flag, proves that a debit
            # committed even if cancellation arrived at the commit boundary.
            amount_to_refund=(await session.execute(update(ServiceOperation).where(
                ServiceOperation.id==op_id,ServiceOperation.state=='running').values(
                    state='failed',http_status=status,response_json=json.dumps({'detail':detail})
                ).returning(ServiceOperation.amount))).scalar_one_or_none()
            if amount_to_refund:
                await credit(session,user_id,amount_to_refund,'refund:'+reason)
            await session.commit()
        await asyncio.shield(settle())
        if isinstance(error,(asyncio.CancelledError,KeyboardInterrupt,SystemExit)):
            raise
        if status==502:
            logger.exception('Service operation failed: %s',scope)
        raise HTTPException(status,detail)


async def recover_expired_scope(session,user_id,scope):
    """Compatibility hook; global maintenance also recovers without a retry."""
    from app.services.maintenance import recover_expired
    return bool(await recover_expired(session, user_id=user_id, scope=scope))
