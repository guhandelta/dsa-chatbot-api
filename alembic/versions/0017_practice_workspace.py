"""Practice workspace: autosaved drafts, checkpoints and test runs."""
from alembic import op
import sqlalchemy as sa

revision = "0017_practice_workspace"
down_revision = "0016_debug_challenges"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "workspace_drafts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("problem_id", sa.String(120), nullable=False),
        sa.Column("language", sa.String(20), nullable=False),
        sa.Column("template", sa.String(40), nullable=False),
        sa.Column("entry", sa.String(64), nullable=False),
        sa.Column("files_json", sa.Text(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "problem_id", "language", name="uq_workspace_draft"),
    )
    op.create_index("ix_workspace_drafts_user_id", "workspace_drafts", ["user_id"])
    op.create_table(
        "workspace_checkpoints",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("problem_id", sa.String(120), nullable=False),
        sa.Column("language", sa.String(20), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("label", sa.String(120), nullable=False),
        sa.Column("entry", sa.String(64), nullable=False),
        sa.Column("files_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_workspace_checkpoints_user_id", "workspace_checkpoints", ["user_id"])
    op.create_index("ix_workspace_checkpoints_created_at", "workspace_checkpoints", ["created_at"])
    op.create_table(
        "workspace_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("problem_id", sa.String(120), nullable=False),
        sa.Column("language", sa.String(20), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("passed_cases", sa.Integer(), nullable=False),
        sa.Column("total_cases", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_workspace_runs_user_id", "workspace_runs", ["user_id"])
    op.create_index("ix_workspace_runs_created_at", "workspace_runs", ["created_at"])


def downgrade():
    op.drop_table("workspace_runs")
    op.drop_table("workspace_checkpoints")
    op.drop_table("workspace_drafts")
