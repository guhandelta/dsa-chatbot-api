"""Persist rubric evidence without changing historical assessment records."""
from alembic import op
import sqlalchemy as sa

revision = '0021_understanding_checks'
down_revision = '0020_practice_session_event_links'
branch_labels = None
depends_on = None


def upgrade():
    for table in ('quiz_answers', 'debug_challenge_attempts'):
        op.add_column(table, sa.Column('understanding_json', sa.Text(), nullable=True))
    op.create_table('understanding_check_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_understanding_check_events_user_id', 'understanding_check_events', ['user_id'])
    op.create_index('ix_understanding_check_events_created_at', 'understanding_check_events', ['created_at'])


def downgrade():
    op.drop_table('understanding_check_events')
    for table in ('debug_challenge_attempts', 'quiz_answers'):
        op.drop_column(table, 'understanding_json')
