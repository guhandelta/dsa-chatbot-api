"""Per-user rate limiting for the expensive endpoints.

WHY
---
`/analyze` runs a sandbox plus two LLM calls; `/mentor/ask` runs one. Neither
had any cap, so a client with a retry bug — or one user in a loop — could burn
unbounded CPU and API spend. Peppercorns bound *deliberate* usage but not
accidental or malicious volume: an admin-granted account, or anyone during a
promotional balance, has effectively unlimited peppercorns.

IMPLEMENTATION
--------------
Counts DEBIT rows in `transactions` within a rolling hour.

An earlier version counted `learning_events` instead, which had two defects
worth recording so they are not reintroduced:

  1. `/analyze` records kind="solved" for a passing submission and
     kind="attempt" for a failing one. Counting only "attempt" meant anyone
     submitting WORKING code was never limited — while still running the
     sandbox and two LLM calls per request. The limit protected against the
     cheap case and ignored the expensive one.

  2. The learning event is written AFTER the pipeline finishes, seconds to a
     minute after the limit check. Concurrent requests all passed the check
     before any of them recorded anything, so the cap was trivially bypassed
     by firing requests in parallel.

Transactions avoid both. Every paid action debits, the debit COMMITS before
the expensive work begins, and the reason field distinguishes action types.
The counter now tracks exactly what costs money.

Residual race: between the check and the debit commit there is a window of
milliseconds. A retry loop can slip one or two extra requests through; it
cannot slip through unbounded ones, because each committed debit immediately
raises the count for every subsequent request. Closing it completely needs a
single atomic check-and-increment (Redis, or a counter row with a conditional
update) — worth doing only if the milliseconds matter.

This is a DATABASE count, not an in-memory one, which is deliberate: it works
across multiple workers and survives restarts. `enforce_rate_limit()` is the
seam if you later move it to Redis.

Limits are per user, not per IP. Every rate-limited endpoint requires
authentication, so the user id is the meaningful subject; IP limiting belongs
at the proxy layer for unauthenticated routes such as login.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import Transaction


class RateLimitExceeded(Exception):
    """Raised when a user exceeds their hourly budget for an action."""


# Maps an action to the transaction `reason` values that represent it.
# Refunds carry the "refund:" prefix and are excluded, so a failed request the
# user was reimbursed for does not consume their budget.
_REASONS: dict[str, tuple[str, ...]] = {
    "attempt": ("analyze",),
    "hint": ("mentor",),
}


def _limit_for(kind: str) -> int:
    """Separate budgets: a review is far more expensive than a hint, so they
    must not share one counter — exhausting reviews should never block the
    mentor."""
    if kind == "hint":
        return settings.hints_per_hour
    return settings.submissions_per_hour


async def count_recent(session: AsyncSession, user_id: str, kind: str,
                       hours: int = 1) -> int:
    """Debits of this action type in the rolling window.

    `amount < 0` restricts the count to debits, so refunds and admin credits
    never inflate a user's usage.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    reasons = _REASONS.get(kind, (kind,))
    stmt = (
        select(func.count())
        .select_from(Transaction)
        .where(
            Transaction.user_id == user_id,
            Transaction.reason.in_(reasons),
            Transaction.amount < 0,
            Transaction.created_at >= cutoff,
        )
    )
    return int((await session.execute(stmt)).scalar_one())


async def enforce_rate_limit(session: AsyncSession, user_id: str, kind: str) -> None:
    """Raise RateLimitExceeded if the user is over budget for this action.

    Checked BEFORE any peppercorn debit, so a rejected request never costs the
    user anything. A limit of 0 or less disables the check entirely.
    """
    limit = _limit_for(kind)
    if limit <= 0:
        return

    used = await count_recent(session, user_id, kind)
    if used >= limit:
        noun = "submissions" if kind == "attempt" else "mentor questions"
        raise RateLimitExceeded(
            f"You've made {used} {noun} in the past hour, which is the limit "
            f"({limit}). This resets on a rolling basis — try again shortly. "
            "No peppercorns were charged."
        )
