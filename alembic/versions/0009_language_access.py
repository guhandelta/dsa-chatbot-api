"""Instructor teaching scope and scoped conversation histories."""
from alembic import op
import sqlalchemy as sa

revision = "0009_language_access"
down_revision = "0008_upload_language"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "instructor_languages",
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("language", sa.String(32), primary_key=True),
        sa.Column("assigned_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.add_column("chat_threads", sa.Column("language", sa.String(32), nullable=False, server_default=""))
    op.add_column("chat_threads", sa.Column("subject", sa.String(80), nullable=False, server_default=""))
    op.add_column("chat_threads", sa.Column("track", sa.String(20), nullable=False, server_default="dsa"))


def downgrade():
    with op.batch_alter_table("chat_threads") as batch:
        batch.drop_column("track")
        batch.drop_column("subject")
        batch.drop_column("language")
    op.drop_table("instructor_languages")
