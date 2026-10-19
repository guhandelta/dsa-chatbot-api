"""Study Room notes: takeaway cards, logged misconceptions and comparisons."""
from alembic import op
import sqlalchemy as sa

revision = "0013_study_notes"
down_revision = "0012_study_quiz"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "study_notes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("language", sa.String(32), nullable=False),
        sa.Column("node_id", sa.String(120), nullable=False),
        sa.Column("mode", sa.String(20), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_study_notes_user_id", "study_notes", ["user_id"])
    op.create_index("ix_study_notes_created_at", "study_notes", ["created_at"])


def downgrade():
    op.drop_table("study_notes")
