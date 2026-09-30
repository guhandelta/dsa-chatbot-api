"""Add knowledge_documents for reviewed /learn uploads.

Revision ID: 0003_knowledge_documents
Revises: 0002_traces
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_knowledge_documents"
down_revision: Union[str, None] = "0002_traces"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False, server_default=".txt"),
        sa.Column("track", sa.String(20), nullable=False, server_default="custom"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending", index=True),
        sa.Column("text", sa.Text, nullable=False, server_default=""),
        sa.Column("characters", sa.Integer, nullable=False, server_default="0"),
        sa.Column("chunk_ids", sa.Text, nullable=False, server_default="[]"),
        sa.Column("review_note", sa.String(500), nullable=False, server_default=""),
        sa.Column("reviewed_by", sa.String(36), nullable=False, server_default=""),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("knowledge_documents")
