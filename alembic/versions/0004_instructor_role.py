"""Rename the `teacher` role to `instructor`.

Revision ID: 0004_instructor_role
Revises: 0003_knowledge_documents

`users.role` is a plain String(20) with no CHECK constraint or enum type, so
this is a data migration with no schema change. It is idempotent — a second
run matches no rows.

Safe to run against a live process: access tokens carry only `sub` and `exp`,
so every request re-reads the role from this table. No one is holding a token
that asserts "teacher", and the gate sees the new value on the next call.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0004_instructor_role"
down_revision: Union[str, None] = "0003_knowledge_documents"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE users SET role = 'instructor' WHERE role = 'teacher'")


def downgrade() -> None:
    op.execute("UPDATE users SET role = 'teacher' WHERE role = 'instructor'")
