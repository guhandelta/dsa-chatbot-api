"""Explicit language scope for new uploads; legacy inference preserves approvals."""
from alembic import op
import sqlalchemy as sa

revision = "0008_upload_language"
down_revision = "0007_vector_cleanup"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("knowledge_documents", sa.Column("language", sa.String(20), nullable=False, server_default=""))


def downgrade():
    with op.batch_alter_table("knowledge_documents") as batch:
        batch.drop_column("language")
