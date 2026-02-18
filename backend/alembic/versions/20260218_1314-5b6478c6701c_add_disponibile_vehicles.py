"""add_disponibile_vehicles

Revision ID: 5b6478c6701c
Revises: 36b4bb1cc982
"""
from alembic import op
import sqlalchemy as sa

revision = '5b6478c6701c'
down_revision = '36b4bb1cc982'

def upgrade():
    with op.batch_alter_table('vehicles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('courtesy_car', sa.Boolean(), nullable=True, server_default=sa.false()))
        batch_op.add_column(sa.Column('disponibile', sa.Boolean(), nullable=True, server_default=sa.true()))

def downgrade():
    with op.batch_alter_table('vehicles', schema=None) as batch_op:
        batch_op.drop_column('courtesy_car')
        batch_op.drop_column('disponibile')
