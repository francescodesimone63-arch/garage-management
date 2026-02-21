"""Merge divergent migration branches

Revision ID: 3d488bb3ba1b
Revises: 7c28deedac76, 20260218_1430_add_contratto
Create Date: 2026-02-20 18:22:45.405074+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d488bb3ba1b'
down_revision: Union[str, None] = ('7c28deedac76', '20260218_1430_add_contratto')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
