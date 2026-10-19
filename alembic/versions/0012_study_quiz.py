"""Study Room quiz sessions and the learner's recorded answers."""
from alembic import op
import sqlalchemy as sa

revision = "0012_study_quiz"
down_revision = "0011_reward_grants"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "quiz_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("language", sa.String(32), nullable=False),
        sa.Column("node_id", sa.String(120), nullable=False),
        sa.Column("items_json", sa.Text(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("answered", sa.Integer(), nullable=False),
        sa.Column("correct", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_quiz_sessions_user_id", "quiz_sessions", ["user_id"])
    op.create_index("ix_quiz_sessions_node_id", "quiz_sessions", ["node_id"])
    op.create_table(
        "quiz_answers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("quiz_id", sa.String(36), sa.ForeignKey("quiz_sessions.id"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("item_id", sa.String(200), nullable=False),
        sa.Column("item_type", sa.String(20), nullable=False),
        sa.Column("concept", sa.String(120), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("correct", sa.Boolean(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("grading", sa.String(20), nullable=False),
        sa.Column("misconception", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("quiz_id", "item_id", name="uq_quiz_answers_quiz_item"),
    )
    for column in ("quiz_id", "user_id", "created_at"):
        op.create_index(f"ix_quiz_answers_{column}", "quiz_answers", [column])


def downgrade():
    op.drop_table("quiz_answers")
    op.drop_table("quiz_sessions")
