"""add system lookup tables

Revision ID: f5ff6ad4a448
Revises: 3e5b1c2f3a4b
Create Date: 2026-02-13 11:50:39.424950+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5ff6ad4a448'
down_revision: Union[str, None] = '3e5b1c2f3a4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
