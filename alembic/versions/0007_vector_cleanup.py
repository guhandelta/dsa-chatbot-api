"""Durable vector deletion outbox; does not change upload approval records."""
from alembic import op
import sqlalchemy as sa

revision = "0007_vector_cleanup"
down_revision = "0006_practice_lock_owner"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("vector_cleanup_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("chunk_ids", sa.Text(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.String(200), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True))
    )


def downgrade():
    op.drop_table("vector_cleanup_jobs")
