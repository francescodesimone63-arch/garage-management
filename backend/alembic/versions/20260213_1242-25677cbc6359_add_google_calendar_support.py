"""add_google_calendar_support

Revision ID: 25677cbc6359
Revises: f5ff6ad4a448
Create Date: 2026-02-13 12:42:36.834164+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25677cbc6359'
down_revision: Union[str, None] = 'f5ff6ad4a448'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add google_event_id column to work_orders table
    op.add_column('work_orders', sa.Column('google_event_id', sa.String(255), nullable=True))
    op.create_index(op.f('ix_work_orders_google_event_id'), 'work_orders', ['google_event_id'], unique=False)
    
    # Create google_oauth_tokens table
    op.create_table(
        'google_oauth_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('access_token_expiry', sa.DateTime(timezone=True), nullable=True),
        sa.Column('calendar_id', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_google_oauth_tokens_id'), 'google_oauth_tokens', ['id'], unique=False)


def downgrade() -> None:
    # Drop google_oauth_tokens table
    op.drop_index(op.f('ix_google_oauth_tokens_id'), table_name='google_oauth_tokens')
    op.drop_table('google_oauth_tokens')
    
    # Remove google_event_id from work_orders
    op.drop_index(op.f('ix_work_orders_google_event_id'), table_name='work_orders')
    op.drop_column('work_orders', 'google_event_id')
