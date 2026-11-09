"""Add append-only student pathway notes separate from assessment events."""
from alembic import op
import sqlalchemy as sa

revision = '0022_student_path_records'
down_revision = '0021_understanding_checks'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("student_path_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("section", sa.String(32), nullable=False),
        sa.Column("language", sa.String(32), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("concept_id", sa.String(120), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("curriculum_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_student_path_records_owner_scope_time", "student_path_records",
                    ["user_id", "section", "language", "created_at"])


def downgrade():
    op.drop_index('ix_student_path_records_owner_scope_time', table_name='student_path_records')
    op.drop_table('student_path_records')
