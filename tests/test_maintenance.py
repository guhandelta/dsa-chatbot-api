from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.db.models import User, ServiceOperation, PracticeSession, Transaction
from app.services.maintenance import recover_expired
from app.services.peppercorns import credit, debit


async def seed(db, *, lock='a'*64, age=31, amount=5):
    user = User(email='recovery@x.com', hashed_password='unused')
    db.add(user)
    await db.flush()
    await credit(db, user.id, 50, 'signup_bonus')
    item = PracticeSession(user_id=user.id, problem_id='two-sum', language='java', provider='gemini', busy=True, busy_token=lock)
    db.add(item)
    await db.flush()
    if amount:
        await debit(db, user.id, amount, 'analyze')
    op = ServiceOperation(id='a'*64, user_id=user.id, scope='practice:'+item.id,
        fingerprint='b'*64, amount=amount, reason='analyze', created_at=datetime.now(timezone.utc)-timedelta(minutes=age))
    db.add(op)
    await db.commit()
    return user.id, item.id


async def test_background_recovery_refunds_once_and_unlocks_only_owner(db):
    uid, sid = await seed(db)
    assert await recover_expired(db) == 1
    assert await recover_expired(db) == 0
    db.expire_all()
    assert (await db.get(User, uid)).peppercorns == 50
    assert not (await db.get(PracticeSession, sid)).busy
    refunds = (await db.scalars(select(Transaction).where(Transaction.reason=='refund:analyze'))).all()
    assert len(refunds) == 1 and refunds[0].amount == 5
    op = await db.get(ServiceOperation, 'a'*64)
    assert op.state == 'failed' and op.http_status == 503


async def test_expired_request_cannot_unlock_newer_action(db):
    uid, sid = await seed(db, lock='newer-action')
    assert await recover_expired(db) == 1
    db.expire_all()
    assert (await db.get(PracticeSession, sid)).busy
    assert (await db.get(PracticeSession, sid)).busy_token == 'newer-action'
    assert (await db.get(User, uid)).peppercorns == 50


async def test_active_request_not_refunded_or_unlocked(db):
    uid, sid = await seed(db, age=29)
    assert await recover_expired(db) == 0
    db.expire_all()
    assert (await db.get(User, uid)).peppercorns == 45
    assert (await db.get(PracticeSession, sid)).busy


async def test_zero_debit_expired_claim_settles_without_credit(db):
    uid, _ = await seed(db, amount=0)
    assert await recover_expired(db) == 1
    db.expire_all()
    assert (await db.get(User, uid)).peppercorns == 50
    assert len((await db.scalars(select(Transaction))).all()) == 1
