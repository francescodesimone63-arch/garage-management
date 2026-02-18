"""add_courtesy_car_vehicles

Revision ID: 36b4bb1cc982  # ← IL TUO ID VERO!
Revises: f6g7h8i9j0k1
"""
from alembic import op
import sqlalchemy as sa

revision = '36b4bb1cc982'  # ← IL TUO ID
down_revision = 'f6g7h8i9j0k1'

def upgrade():
    op.add_column('vehicles', sa.Column('courtesy_car', sa.Boolean(), server_default='false'))

def downgrade():
    op.drop_column('vehicles', 'courtesy_car')
