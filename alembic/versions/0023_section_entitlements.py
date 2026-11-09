"""Stage section rights separately from legacy language subscriptions."""
from alembic import op
import sqlalchemy as sa

revision = '0023_section_entitlements'
down_revision = '0022_student_path_records'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("section_entitlements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("section", sa.String(32), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("source", sa.String(30), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_section_entitlements_owner_section", "section_entitlements", ["user_id", "section"])


def downgrade():
    op.drop_index("ix_section_entitlements_owner_section", table_name="section_entitlements")
    op.drop_table("section_entitlements")
