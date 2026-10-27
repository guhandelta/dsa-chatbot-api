"""Bind new practice events and evaluations to their graph session."""
from alembic import op
import sqlalchemy as sa

revision = "0020_practice_session_event_links"
down_revision = "0019_timestamp_constraints"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("learning_events", sa.Column("practice_session_id", sa.String(36), nullable=True))
    op.create_index("ix_learning_events_practice_session_id", "learning_events", ["practice_session_id"])
    op.add_column("workspace_runs", sa.Column("practice_session_id", sa.String(36), nullable=True))
    op.create_index("ix_workspace_runs_practice_session_id", "workspace_runs", ["practice_session_id"])


def downgrade():
    op.drop_index("ix_workspace_runs_practice_session_id", table_name="workspace_runs")
    op.drop_column("workspace_runs", "practice_session_id")
    op.drop_index("ix_learning_events_practice_session_id", table_name="learning_events")
    op.drop_column("learning_events", "practice_session_id")
