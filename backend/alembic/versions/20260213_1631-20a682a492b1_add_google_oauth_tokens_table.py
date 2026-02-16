"""add google_oauth_tokens table

Revision ID: 20a682a492b1
Revises: 25677cbc6359
Create Date: 2026-02-13 16:31:08.193279+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20a682a492b1'
down_revision: Union[str, None] = '25677cbc6359'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'google_oauth_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('access_token_expiry', sa.DateTime(timezone=True), nullable=True),
        sa.Column('calendar_id', sa.String(255), nullable=False, server_default='primary'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('google_oauth_tokens')
