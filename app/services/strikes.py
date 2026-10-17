"""Three-strike enforcement for malicious code submissions.

POLICY (configurable via .env)
------------------------------
  Strike 1  warning, submission refused before charging
  Strike 2  final warning, submission refused before charging
  Strike 3  account suspended; existing balance is preserved

Only a `block` verdict from the screener counts as a strike. A `warn`
(suspicious but plausibly a beginner mistake — an accidental infinite loop, a
stray `eval`) refuses the run and is logged, but never accumulates toward
suspension. This matters: the cost of wrongly suspending a paying learner is
much higher than the cost of letting an ambiguous submission through to a
sandbox that already assumes hostility.

Every event is recorded in `security_events` regardless of outcome, so a human
can audit and reverse a suspension. Automated punishment without an appeal
trail is indefensible, and "the classifier said so" is not a reason a support
agent can give a customer.
"""
import json

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import SecurityEvent, User
from app.services.code_screener import ScreenResult


class AccountSuspendedError(Exception):
    """Raised when a suspended account attempts a restricted action."""


def assert_active(user: User) -> None:
    if user.status != "active":
        raise AccountSuspendedError(
            user.suspended_reason
            or "This account is suspended. Contact support if you believe "
               "this is a mistake."
        )


async def record_event(
    session: AsyncSession,
    user: User,
    result: ScreenResult,
    code: str,
    context: str = "analyze",
) -> dict:
    """Logs a screening failure and applies the strike policy.

    Returns a dict describing what the user should be told. Does not commit —
    the caller owns the transaction boundary.
    """
    counts_as_strike = result.is_violation

    session.add(
        SecurityEvent(
            user_id=user.id,
            severity=result.verdict,
            reasons=json.dumps(result.reasons),
            matched_rules=json.dumps(result.matched_rules),
            # Store a bounded excerpt only — enough for a human to judge,
            # not a full copy of everything a user ever submitted.
            code_excerpt=code[:2000],
            context=context,
            counted_as_strike=counts_as_strike,
        )
    )

    if not counts_as_strike:
        return {
            "strike_applied": False,
            "strikes": user.strikes,
            "suspended": False,
        }

    new_count = (await session.execute(update(User).where(User.id == user.id)
        .values(strikes=User.strikes + 1).returning(User.strikes))).scalar_one()
    suspend = new_count >= settings.max_strikes
    if suspend:
        reason = f"Account suspended after {new_count} blocked submissions containing prohibited operations."
        await session.execute(update(User).where(User.id == user.id).values(status="suspended", suspended_reason=reason))
        user.status = "suspended"
        user.suspended_reason = reason
    user.strikes = new_count

    remaining = max(settings.max_strikes - new_count, 0)
    return {
        "strike_applied": True,
        "strikes": new_count,
        "max_strikes": settings.max_strikes,
        "remaining": remaining,
        "suspended": suspend,
        "message": (
            "Your account has been suspended for repeatedly submitting code "
            "with prohibited operations. Your balance is preserved, but spending "
            "is disabled. Contact support if you believe this is an error."
            if suspend else
            f"This submission was blocked. Strike {new_count} of "
            f"{settings.max_strikes} — {remaining} more will suspend your "
            "account. Your balance is preserved during suspension."
        ),
    }


async def list_events(session: AsyncSession, user_id: str | None = None) -> list[SecurityEvent]:
    stmt = select(SecurityEvent).order_by(SecurityEvent.created_at.desc())
    if user_id:
        stmt = stmt.where(SecurityEvent.user_id == user_id)
    return list((await session.execute(stmt)).scalars())


async def reinstate(session: AsyncSession, user: User) -> None:
    """Admin override: clears the suspension and resets the counter.
    The security_events rows are deliberately retained."""
    await session.execute(
        update(User)
        .where(User.id == user.id)
        .values(status="active", strikes=0, suspended_reason="")
    )
    user.status = "active"
    user.strikes = 0
    user.suspended_reason = ""
