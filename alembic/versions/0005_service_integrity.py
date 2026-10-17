"""Durable service receipts and transactional practice checkpoints."""
from alembic import op
import sqlalchemy as sa

revision = "0005_service_integrity"
down_revision = "0004_instructor_role"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("subscriptions", sa.Column("provider_event_timestamp", sa.Integer(), nullable=False, server_default="0"))
    op.execute("UPDATE learning_events SET kind = 'reflection' WHERE kind = 'solved' AND reasoning <> ''")
    op.create_table("service_operations",
        sa.Column("id",sa.String(64),primary_key=True),
        sa.Column("user_id",sa.String(36),sa.ForeignKey("users.id"),nullable=False),
        sa.Column("scope",sa.String(100),nullable=False),
        sa.Column("fingerprint",sa.String(64),nullable=False),
        sa.Column("state",sa.String(20),nullable=False),
        sa.Column("amount",sa.Integer(),nullable=False),
        sa.Column("reason",sa.String(100),nullable=False),
        sa.Column("http_status",sa.Integer(),nullable=False),
        sa.Column("response_json",sa.Text(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_index("ix_service_operations_user_id","service_operations",["user_id"])
    op.create_table("practice_sessions",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("user_id",sa.String(36),sa.ForeignKey("users.id"),nullable=False),
        sa.Column("problem_id",sa.String(120),nullable=False),
        sa.Column("language",sa.String(20),nullable=False),
        sa.Column("provider",sa.String(20),nullable=False),
        sa.Column("busy",sa.Boolean(),nullable=False),
        sa.Column("status",sa.String(20),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_index("ix_practice_sessions_user_id","practice_sessions",["user_id"])
    op.create_table("practice_checkpoints",
        sa.Column("id",sa.String(64),primary_key=True),
        sa.Column("thread_id",sa.String(255),nullable=False),
        sa.Column("namespace",sa.String(255),nullable=False),
        sa.Column("checkpoint_id",sa.String(64),nullable=False),
        sa.Column("parent_id",sa.String(64),nullable=False),
        sa.Column("checkpoint_data",sa.Text(),nullable=False),
        sa.Column("metadata_data",sa.Text(),nullable=False),
        sa.Column("writes_json",sa.Text(),nullable=False),
    )
    op.create_index("ix_practice_checkpoints_thread_id","practice_checkpoints",["thread_id"])
    op.create_table("webhook_receipts",
        sa.Column("id",sa.String(255),primary_key=True),
        sa.Column("payload_hash",sa.String(64),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )


def downgrade():
    op.execute("UPDATE learning_events SET kind = 'solved' WHERE kind = 'reflection'")
    with op.batch_alter_table("subscriptions") as batch:
        batch.drop_column("provider_event_timestamp")
    op.drop_table("webhook_receipts")
    op.drop_table("practice_checkpoints")
    op.drop_table("practice_sessions")
    op.drop_table("service_operations")
