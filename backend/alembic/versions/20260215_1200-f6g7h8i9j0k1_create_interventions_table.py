"""Create interventions table

Revision ID: f6g7h8i9j0k1
Revises: 20a682a492b1
Create Date: 2026-02-15 12:00:00.000000+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6g7h8i9j0k1'
down_revision: Union[str, None] = '20a682a492b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
    # Add tipo_danno column back to work_orders
    op.add_column('work_orders', sa.Column('tipo_danno', sa.String(length=50), nullable=True))
    
    # Drop interventions table
    op.drop_index('ix_interventions_work_order_id', table_name='interventions')
    op.drop_index('ix_interventions_id', table_name='interventions')
    op.drop_table('interventions')
