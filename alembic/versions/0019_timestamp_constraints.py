"""Align legacy timestamp constraints with the ORM, preserving existing indexes."""
from alembic import op
import sqlalchemy as sa

revision = '0019_timestamp_constraints'
down_revision = '0018_learning_strikes'
branch_labels = None
depends_on = None

COLUMNS = (
    ('chat_messages', 'created_at'), ('chat_threads', 'created_at'),
    ('knowledge_documents', 'created_at'), ('knowledge_documents', 'updated_at'),
    ('learning_events', 'created_at'), ('security_events', 'created_at'),
    ('submissions', 'created_at'), ('subscriptions', 'started_at'),
    ('trace_records', 'created_at'), ('transactions', 'created_at'),
    ('users', 'created_at'), ('vector_cleanup_jobs', 'created_at'),
)


def upgrade():
    for table, column in COLUMNS:
        # Legacy rows may lack timestamps; preserve the rows and give them the
        # migration time before enforcing the ORM's existing NOT NULL contract.
        op.execute(sa.text(f'UPDATE {table} SET {column} = CURRENT_TIMESTAMP WHERE {column} IS NULL'))
        with op.batch_alter_table(table) as batch:
            batch.alter_column(column, existing_type=sa.DateTime(timezone=True), nullable=False)


def downgrade():
    for table, column in reversed(COLUMNS):
        with op.batch_alter_table(table) as batch:
            batch.alter_column(column, existing_type=sa.DateTime(timezone=True), nullable=True)
