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
    # Create interventions table
    op.create_table(
        'interventions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('work_order_id', sa.Integer(), nullable=False),
        sa.Column('progressivo', sa.Integer(), nullable=False),
        sa.Column('descrizione_intervento', sa.Text(), nullable=False),
        sa.Column('durata_stimata', sa.DECIMAL(precision=4, scale=2), nullable=False, server_default='0'),
        sa.Column('tipo_intervento', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['work_order_id'], ['work_orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_interventions_id', 'interventions', ['id'], unique=False)
    op.create_index('ix_interventions_work_order_id', 'interventions', ['work_order_id'], unique=False)
    
    # Drop tipo_danno column from work_orders
    op.drop_column('work_orders', 'tipo_danno')


def downgrade() -> None:
    # Add tipo_danno column back to work_orders
    op.add_column('work_orders', sa.Column('tipo_danno', sa.String(length=50), nullable=True))
    
    # Drop interventions table
    op.drop_index('ix_interventions_work_order_id', table_name='interventions')
    op.drop_index('ix_interventions_id', table_name='interventions')
    op.drop_table('interventions')
