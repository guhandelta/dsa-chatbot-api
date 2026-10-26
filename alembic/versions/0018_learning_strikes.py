"""Learning strikes, their clearing challenge sets, and extra practice."""
from alembic import op
import sqlalchemy as sa

revision = "0018_learning_strikes"
down_revision = "0017_practice_workspace"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "challenge_sets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("language", sa.String(32), nullable=False),
        sa.Column("node_id", sa.String(120), nullable=False),
        sa.Column("problem_id", sa.String(120), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("items_json", sa.Text(), nullable=False),
        sa.Column("required", sa.Integer(), nullable=False),
        sa.Column("correct", sa.Integer(), nullable=False),
        sa.Column("answered", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_challenge_sets_user_id", "challenge_sets", ["user_id"])
    op.create_index("ix_challenge_sets_created_at", "challenge_sets", ["created_at"])
    op.create_table(
        "challenge_answers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("set_id", sa.String(36), sa.ForeignKey("challenge_sets.id"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("item_id", sa.String(200), nullable=False),
        sa.Column("item_type", sa.String(20), nullable=False),
        sa.Column("concept", sa.String(120), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("correct", sa.Boolean(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("set_id", "item_id", name="uq_challenge_answer_item"),
    )
    op.create_index("ix_challenge_answers_set_id", "challenge_answers", ["set_id"])
    op.create_index("ix_challenge_answers_user_id", "challenge_answers", ["user_id"])
    op.create_index("ix_challenge_answers_created_at", "challenge_answers", ["created_at"])
    op.create_table(
        "learning_strikes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("language", sa.String(32), nullable=False),
        sa.Column("problem_id", sa.String(120), nullable=False),
        sa.Column("node_id", sa.String(120), nullable=False),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("where_json", sa.Text(), nullable=False),
        sa.Column("set_id", sa.String(36), sa.ForeignKey("challenge_sets.id"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cleared_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_learning_strikes_user_id", "learning_strikes", ["user_id"])
    op.create_index("ix_learning_strikes_created_at", "learning_strikes", ["created_at"])


def downgrade():
    op.drop_table("learning_strikes")
    op.drop_table("challenge_answers")
    op.drop_table("challenge_sets")
