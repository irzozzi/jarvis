"""add indexes for context stats

Revision ID: e2836d7fdc3b
Revises: 0481f1d6b66f
Create Date: 2026-04-07 12:32:16.670571

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2836d7fdc3b'
down_revision: Union[str, Sequence[str], None] = '0481f1d6b66f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_index('ix_habit_logs_context_id', 'habit_logs', ['context_id'])
    op.create_index('ix_habit_logs_completed_at', 'habit_logs', ['completed_at'])
    op.create_index('ix_habit_logs_habit_id', 'habit_logs', ['habit_id'])
    op.create_index('ix_context_user_id', 'context', ['user_id'])
    op.create_index('ix_context_timestamp', 'context', ['timestamp'])

def downgrade():
    op.drop_index('ix_context_timestamp')
    op.drop_index('ix_context_user_id')
    op.drop_index('ix_habit_logs_habit_id')
    op.drop_index('ix_habit_logs_completed_at')
    op.drop_index('ix_habit_logs_context_id')
