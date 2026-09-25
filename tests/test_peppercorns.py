# Unit tests for the peppercorn ledger: atomic debits, refunds, and the
# guarantee that you can't spend below zero.
import pytest

from app.db.models import Transaction, User
from app.services.peppercorns import (
    InsufficientPeppercornsError,
    credit,
    debit,
)
from sqlalchemy import select


async def _make_user(db, balance=0):
    user = User(email="a@b.com", hashed_password="x", peppercorns=balance)
    db.add(user)
    await db.flush()
    return user


async def test_credit_increases_balance_and_logs(db):
    user = await _make_user(db, 0)
    new_balance = await credit(db, user.id, 50, reason="signup_bonus")
    await db.commit()
    assert new_balance == 50

    rows = (await db.execute(select(Transaction).where(Transaction.user_id == user.id))).scalars().all()
    assert len(rows) == 1
    assert rows[0].amount == 50
    assert rows[0].balance_after == 50
    assert rows[0].reason == "signup_bonus"


async def test_debit_reduces_balance(db):
    user = await _make_user(db, 10)
    new_balance = await debit(db, user.id, 3, reason="chat")
    await db.commit()
    assert new_balance == 7


async def test_debit_insufficient_raises_and_leaves_balance(db):
    user = await _make_user(db, 2)
    with pytest.raises(InsufficientPeppercornsError):
        await debit(db, user.id, 5, reason="analyze")
    await db.rollback()
    refreshed = await db.get(User, user.id)
    assert refreshed.peppercorns == 2  # unchanged


async def test_debit_exact_balance_allowed(db):
    user = await _make_user(db, 5)
    new_balance = await debit(db, user.id, 5, reason="analyze")
    await db.commit()
    assert new_balance == 0


async def test_debit_then_refund_restores_balance(db):
    user = await _make_user(db, 10)
    await debit(db, user.id, 5, reason="analyze")
    await db.commit()
    after_refund = await credit(db, user.id, 5, reason="refund:analyze")
    await db.commit()
    assert after_refund == 10
    rows = (await db.execute(select(Transaction).where(Transaction.user_id == user.id))).scalars().all()
    assert [r.amount for r in rows] == [-5, 5]


async def test_negative_amounts_rejected(db):
    user = await _make_user(db, 10)
    with pytest.raises(ValueError):
        await debit(db, user.id, 0, reason="x")
    with pytest.raises(ValueError):
        await credit(db, user.id, -1, reason="x")
