"""Add trace_records for observability.

Revision ID: 0002_traces
Revises: 0001_initial
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_traces"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "trace_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("trace_id", sa.String(32), nullable=False, index=True),
        sa.Column("name", sa.String(60), nullable=False, index=True),
        sa.Column("user_id", sa.String(36), nullable=False, server_default="", index=True),
        sa.Column("duration_ms", sa.Float, nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="ok"),
        sa.Column("total_tokens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("estimated_cost_usd", sa.Float, nullable=False, server_default="0"),
        sa.Column("payload", sa.Text, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    # Pruning and the summary view both scan by recency.
    op.create_index("ix_trace_records_created", "trace_records", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_trace_records_created", table_name="trace_records")
    op.drop_table("trace_records")
