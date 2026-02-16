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
    # Create damage_types table
    op.create_table(
        'damage_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('descrizione', sa.Text(), nullable=True),
        sa.Column('attivo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nome')
    )
    op.create_index(op.f('ix_damage_types_id'), 'damage_types', ['id'])
    op.create_index(op.f('ix_damage_types_nome'), 'damage_types', ['nome'])

    # Create customer_types table
    op.create_table(
        'customer_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(50), nullable=False),
        sa.Column('descrizione', sa.Text(), nullable=True),
        sa.Column('attivo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nome')
    )
    op.create_index(op.f('ix_customer_types_id'), 'customer_types', ['id'])
    op.create_index(op.f('ix_customer_types_nome'), 'customer_types', ['nome'])

    # Create work_order_status_types table
    op.create_table(
        'work_order_status_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(50), nullable=False),
        sa.Column('descrizione', sa.Text(), nullable=True),
        sa.Column('attivo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nome')
    )
    op.create_index(op.f('ix_work_order_status_types_id'), 'work_order_status_types', ['id'])
    op.create_index(op.f('ix_work_order_status_types_nome'), 'work_order_status_types', ['nome'])

    # Create priority_types table
    op.create_table(
        'priority_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(50), nullable=False),
        sa.Column('descrizione', sa.Text(), nullable=True),
        sa.Column('attivo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nome')
    )
    op.create_index(op.f('ix_priority_types_id'), 'priority_types', ['id'])
    op.create_index(op.f('ix_priority_types_nome'), 'priority_types', ['nome'])


def downgrade() -> None:
    op.drop_index(op.f('ix_priority_types_nome'), 'priority_types')
    op.drop_index(op.f('ix_priority_types_id'), 'priority_types')
    op.drop_table('priority_types')
    op.drop_index(op.f('ix_work_order_status_types_nome'), 'work_order_status_types')
    op.drop_index(op.f('ix_work_order_status_types_id'), 'work_order_status_types')
    op.drop_table('work_order_status_types')
    op.drop_index(op.f('ix_customer_types_nome'), 'customer_types')
    op.drop_index(op.f('ix_customer_types_id'), 'customer_types')
    op.drop_table('customer_types')
    op.drop_index(op.f('ix_damage_types_nome'), 'damage_types')
    op.drop_index(op.f('ix_damage_types_id'), 'damage_types')
    op.drop_table('damage_types')
