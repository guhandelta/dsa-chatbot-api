"""Pin Study Room conversation focus and comparison language."""
from alembic import op
import sqlalchemy as sa

revision = "0015_study_thread_focus"
down_revision = "0014_hint_billing"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("chat_threads", sa.Column("study_focus_id", sa.String(120), nullable=False, server_default=""))
    op.add_column("chat_threads", sa.Column("compare_language", sa.String(32), nullable=False, server_default=""))


def downgrade():
    with op.batch_alter_table("chat_threads") as batch:
        batch.drop_column("compare_language")
        batch.drop_column("study_focus_id")
