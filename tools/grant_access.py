#!/usr/bin/env python3
"""Grant one account full access — the local "God mode" override.

    python tools/grant_access.py you@example.com
    python tools/grant_access.py you@example.com --peppercorns 100000 --days 3650
    python tools/grant_access.py --list

WHY THIS EXISTS
---------------
Three independent gates control what an account can do, and being an admin
only clears the first:

  1. role          — admin/teacher unlocks /train and /admin
  2. entitlements  — a per-LANGUAGE subscription unlocks the Socratic mentor
  3. peppercorns   — every chat, review, and mentor turn costs them

So an admin with 50 peppercorns and no subscription still cannot use the
mentor and runs out of balance after a few reviews. This script clears all
three at once, plus lifts any suspension.

It writes directly to the database rather than going through the API,
deliberately: it has to work when you are locked out, which is exactly when
an API-based tool would not.

LOCAL USE ONLY. There is no authentication here — anyone who can run this
file owns every account in the database. That is fine on your laptop and
unacceptable on a server. Do not ship it in a deployed image.
"""
import argparse
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import SessionLocal  # noqa: E402
from app.db.models import Subscription, Transaction, User  # noqa: E402

LANGUAGES = ["python", "javascript", "java", "cpp", "c", "rust"]


async def list_users() -> int:
    async with SessionLocal() as session:
        users = list((await session.execute(select(User).order_by(User.created_at))).scalars())
        if not users:
            print(
                "\nNo accounts exist yet.\n\n"
                "Nothing is seeded — you create the first account by registering:\n"
                "  1. Start the API and UI\n"
                "  2. Open http://localhost:3000/register\n"
                "  3. Sign up with the email in ADMIN_EMAILS\n"
                "  4. Re-run this script with that email\n"
            )
            return 1
        print(f"\n{len(users)} account(s):\n")
        for u in users:
            subs = list((await session.execute(
                select(Subscription).where(
                    Subscription.user_id == u.id, Subscription.status == "active"
                )
            )).scalars())
            langs = ",".join(s.language for s in subs) or "none"
            print(f"  {u.email:32} role={u.role:8} status={u.status:10} "
                  f"peppercorns={u.peppercorns:<8} mentor={langs}")
        print()
        return 0


async def grant(email: str, peppercorns: int, days: int) -> int:
    email = email.strip().lower()
    async with SessionLocal() as session:
        user = (await session.execute(
            select(User).where(User.email == email)
        )).scalar_one_or_none()

        if user is None:
            print(
                f"\nNo account found for '{email}'.\n\n"
                "Accounts are created by registering — nothing is pre-seeded.\n"
                "  1. Open http://localhost:3000/register\n"
                "  2. Sign up with this email\n"
                "  3. Re-run this script\n\n"
                "Run with --list to see which accounts do exist.\n"
            )
            return 1

        before = (user.role, user.peppercorns, user.status)

        # 1. role
        user.role = "admin"

        # 2. peppercorns — write a ledger row too, so the balance and the
        #    transaction history stay consistent. A balance that does not
        #    reconcile against the ledger is a debugging nightmare later.
        delta = peppercorns - user.peppercorns
        if delta != 0:
            user.peppercorns = peppercorns
            session.add(Transaction(
                user_id=user.id, amount=delta, balance_after=peppercorns,
                reason="admin_grant:local_access",
            ))

        # 3. lift any suspension
        user.status = "active"
        user.strikes = 0
        user.suspended_reason = ""

        # 4. mentor subscription for every language
        expires = datetime.now(timezone.utc) + timedelta(days=days)
        existing = {
            s.language: s for s in (await session.execute(
                select(Subscription).where(Subscription.user_id == user.id)
            )).scalars()
        }
        for language in LANGUAGES:
            if language in existing:
                sub = existing[language]
                sub.status = "active"
                sub.expires_at = expires
                session.add(sub)
            else:
                session.add(Subscription(
                    user_id=user.id, language=language, status="active",
                    expires_at=expires, provider_ref="local-grant",
                ))

        session.add(user)
        await session.commit()

        print(f"\nFull access granted to {email}\n")
        print(f"  role         {before[0]} -> admin")
        print(f"  peppercorns  {before[1]} -> {peppercorns}")
        print(f"  status       {before[2]} -> active (strikes cleared)")
        print(f"  mentor       all {len(LANGUAGES)} languages, until {expires:%Y-%m-%d}")
        print("\nLog out and back in so the UI picks up the new role.\n")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Grant full local access to one account.",
    )
    parser.add_argument("email", nargs="?", help="account email (must already be registered)")
    parser.add_argument("--peppercorns", type=int, default=1_000_000,
                        help="balance to set (default: 1000000)")
    parser.add_argument("--days", type=int, default=3650,
                        help="mentor subscription length in days (default: 3650)")
    parser.add_argument("--list", action="store_true", help="list existing accounts")
    args = parser.parse_args()

    if args.list:
        return asyncio.run(list_users())
    if not args.email:
        parser.print_help()
        print("\nTip: run with --list to see which accounts exist.\n")
        return 1
    return asyncio.run(grant(args.email, args.peppercorns, args.days))


if __name__ == "__main__":
    sys.exit(main())
