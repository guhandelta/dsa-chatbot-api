"""Transaction-scoped per-learner serialization on SQLite and PostgreSQL."""
from sqlalchemy import update
from app.db.models import User


async def lock_user(session, user_id):
    # A write locks the row on PostgreSQL and the writer on SQLite. Call before
    # reading counters/revisions, and hold until the feature transaction commits.
    await session.execute(update(User).where(User.id == user_id).values(
        profile_generation=User.profile_generation))
