"""Durable administrative action history."""
from alembic import op
import sqlalchemy as sa

revision = "0010_admin_audit"
down_revision = "0009_language_access"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admin_audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("actor_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(60), nullable=False),
        sa.Column("target_id", sa.String(120), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("before_json", sa.Text(), nullable=False),
        sa.Column("after_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    for column in ("actor_id", "action", "target_id", "created_at"):
        op.create_index(f"ix_admin_audit_events_{column}", "admin_audit_events", [column])


def downgrade():
    op.drop_table("admin_audit_events")
