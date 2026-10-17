"""Identify the owner of a practice action lock, including during recovery."""
from alembic import op
import sqlalchemy as sa

revision = "0006_practice_lock_owner"
down_revision = "0005_service_integrity"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("practice_sessions", sa.Column("busy_token", sa.String(64), nullable=False, server_default=""))


def downgrade():
    with op.batch_alter_table("practice_sessions") as batch:
        batch.drop_column("busy_token")
