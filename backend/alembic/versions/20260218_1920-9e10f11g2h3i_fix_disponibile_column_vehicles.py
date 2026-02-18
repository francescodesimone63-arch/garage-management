"""fix_disponibile_column_vehicles

Revision ID: 9e10f11g2h3i
Revises: 5b6478c6701c
"""
from alembic import op
import sqlalchemy as sa

revision = '9e10f11g2h3i'
down_revision = '5b6478c6701c'

def upgrade():
    # SQLite doesn't support many DDL operations, so we need to use batch_alter_table
    # But first, we need to handle the problematic FK by recreating the table
    with op.batch_alter_table('vehicles', schema=None, recreate='always') as batch_op:
        # Drop the problematic column
        batch_op.drop_column('stato_disponibilita_id')
        
        # Add disponibile column with TRUE as default (vehicle is available by default)
        batch_op.add_column(sa.Column('disponibile', sa.Boolean(), nullable=True, server_default=sa.true()))

def downgrade():
    with op.batch_alter_table('vehicles', schema=None, recreate='always') as batch_op:
        batch_op.drop_column('disponibile')

