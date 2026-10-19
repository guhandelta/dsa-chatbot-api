"""Earn-back peppercorn rewards, granted at most once per key."""
from alembic import op
import sqlalchemy as sa

revision = "0011_reward_grants"
down_revision = "0010_admin_audit"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "reward_grants",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("key", sa.String(200), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "key", name="uq_reward_grants_user_key"),
    )
    op.create_index("ix_reward_grants_user_id", "reward_grants", ["user_id"])


def downgrade():
    op.drop_table("reward_grants")
