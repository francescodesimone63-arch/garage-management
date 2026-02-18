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
    pass


def downgrade() -> None:
    pass
