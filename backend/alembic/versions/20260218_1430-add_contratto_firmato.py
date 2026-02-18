"""add_contratto_firmato column to courtesy_cars

Revision ID: 20260218_1430
Revises: 20260218_1920
Create Date: 2026-02-18 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260218_1430_add_contratto'
down_revision = '9e10f11g2h3i'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Aggiungi colonna contratto_firmato
    op.add_column('courtesy_cars', sa.Column('contratto_firmato', sa.String(500), nullable=True))


def downgrade() -> None:
    # Rimuovi colonna contratto_firmato
    op.drop_column('courtesy_cars', 'contratto_firmato')
