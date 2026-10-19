"""Retain minimal hint billing history and reserve tiers before generation."""
from alembic import op
import sqlalchemy as sa

revision = "0014_hint_billing"
down_revision = "0013_study_notes"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("profile_generation", sa.Integer(), nullable=False, server_default="0"))
    usage = op.create_table(
        "hint_usage",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("problem_id", sa.String(120), nullable=False),
        sa.Column("language", sa.String(32), nullable=False),
        sa.Column("tier", sa.Integer(), nullable=False),
        sa.Column("operation_id", sa.String(64), sa.ForeignKey("service_operations.id"), unique=True),
        sa.Column("event_id", sa.String(36), unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_hint_usage_user_id", "hint_usage", ["user_id"])
    events = sa.table("learning_events", sa.column("id"), sa.column("user_id"),
                      sa.column("problem_id"), sa.column("language"), sa.column("hint_tier"),
                      sa.column("kind"), sa.column("created_at"))
    op.get_bind().execute(usage.insert().from_select(
        ["id", "user_id", "problem_id", "language", "tier", "event_id", "created_at"],
        sa.select(events.c.id, events.c.user_id, events.c.problem_id, events.c.language,
                  events.c.hint_tier, events.c.id, events.c.created_at).where(events.c.kind == "hint")))


def downgrade():
    op.drop_table("hint_usage")
    with op.batch_alter_table("users") as batch:
        batch.drop_column("profile_generation")
