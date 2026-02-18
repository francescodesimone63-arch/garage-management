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
    pass


def downgrade() -> None:
    pass
