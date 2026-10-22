"""Persistent, non-repeating debugging challenge assignments."""
from alembic import op
import sqlalchemy as sa

revision = "0016_debug_challenges"
down_revision = "0015_study_thread_focus"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "debug_challenge_attempts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("challenge_id", sa.String(80), nullable=False),
        sa.Column("language", sa.String(32), nullable=False),
        sa.Column("subject", sa.String(80), nullable=False),
        sa.Column("difficulty", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("diagnosis", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "challenge_id", name="uq_debug_challenge_user_problem"),
    )
    op.create_index("ix_debug_challenge_attempts_user_id", "debug_challenge_attempts", ["user_id"])


def downgrade():
    op.drop_table("debug_challenge_attempts")
