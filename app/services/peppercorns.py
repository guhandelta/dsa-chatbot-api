# Peppercorn economy: atomic debits/credits + an append-only ledger.
#
# Debits use a conditional UPDATE (balance must cover the amount) so two
# concurrent requests can never spend the same peppercorns. The pattern is
# portable: it works identically on SQLite and Postgres.
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Transaction, User


class InsufficientPeppercornsError(Exception):
    """Raised when a user tries to spend more peppercorns than they have."""


async def debit(session: AsyncSession, user_id: str, amount: int, reason: str) -> int:
    """Atomically deduct `amount` peppercorns. Returns the new balance.

    Raises InsufficientPeppercornsError if the balance can't cover it.
    Does NOT commit — the caller owns the transaction boundary.
    """
    if amount <= 0:
        raise ValueError("Debit amount must be positive")

    result = await session.execute(
        update(User)
        .where(User.id == user_id, User.peppercorns >= amount)
        .values(peppercorns=User.peppercorns - amount)
        .returning(User.peppercorns)
    )
    new_balance = result.scalar_one_or_none()
    if new_balance is None:
        raise InsufficientPeppercornsError(
            f"Insufficient peppercorns: this action costs {amount}."
        )

    session.add(
        Transaction(user_id=user_id, amount=-amount, balance_after=new_balance, reason=reason)
    )
    return new_balance


async def credit(session: AsyncSession, user_id: str, amount: int, reason: str) -> int:
    """Add peppercorns (signup bonus, refunds, future purchases). Returns new balance."""
    if amount <= 0:
        raise ValueError("Credit amount must be positive")

    result = await session.execute(
        update(User)
        .where(User.id == user_id)
        .values(peppercorns=User.peppercorns + amount)
        .returning(User.peppercorns)
    )
    new_balance = result.scalar_one()
    session.add(
        Transaction(user_id=user_id, amount=amount, balance_after=new_balance, reason=reason)
    )
    return new_balance
