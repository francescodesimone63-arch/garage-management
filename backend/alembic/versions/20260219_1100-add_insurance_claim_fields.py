"""Add insurance claim fields to work_orders

Revision ID: add_insurance_claims
Revises: 9e10f11g2h3i
Create Date: 2026-02-19 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# Revision identifiers, used by Alembic.
revision = 'add_insurance_claims'
down_revision = '9e10f11g2h3i'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create insurance_branch_types lookup table only if it doesn't exist
    ctx = op.get_context()
    inspector = inspect(ctx.bind)
    
    if 'insurance_branch_types' not in inspector.get_table_names():
        op.create_table(
            'insurance_branch_types',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('nome', sa.String(100), nullable=False, unique=True),
            sa.Column('codice', sa.String(30), nullable=False, unique=True),
            sa.Column('descrizione', sa.Text(), nullable=True),
            sa.Column('attivo', sa.Boolean(), nullable=False, server_default='1'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id', name=op.f('pk_insurance_branch_types')),
            sa.UniqueConstraint('nome', name=op.f('uq_insurance_branch_types_nome')),
            sa.UniqueConstraint('codice', name=op.f('uq_insurance_branch_types_codice')),
        )
        op.create_index(op.f('ix_insurance_branch_types_nome'), 'insurance_branch_types', ['nome'], unique=True)
        op.create_index(op.f('ix_insurance_branch_types_codice'), 'insurance_branch_types', ['codice'], unique=True)

    # SQLite batch mode for schema changes
    columns = [col['name'] for col in inspector.get_columns('work_orders')]
    
    with op.batch_alter_table('work_orders', schema=None) as batch_op:
        # Add insurance claim fields to work_orders only if they don't exist
        if 'sinistro' not in columns:
            batch_op.add_column(sa.Column('sinistro', sa.Boolean(), nullable=False, server_default='0'))
        if 'ramo_sinistro_id' not in columns:
            batch_op.add_column(sa.Column('ramo_sinistro_id', sa.Integer(), nullable=True))
        if 'legale' not in columns:
            batch_op.add_column(sa.Column('legale', sa.Text(), nullable=True))
        if 'autorita' not in columns:
            batch_op.add_column(sa.Column('autorita', sa.Text(), nullable=True))
        if 'numero_sinistro' not in columns:
            batch_op.add_column(sa.Column('numero_sinistro', sa.String(50), nullable=True))
        if 'compagnia_sinistro' not in columns:
            batch_op.add_column(sa.Column('compagnia_sinistro', sa.String(200), nullable=True))
        if 'compagnia_debitrice_sinistro' not in columns:
            batch_op.add_column(sa.Column('compagnia_debitrice_sinistro', sa.String(200), nullable=True))
        if 'scoperto' not in columns:
            batch_op.add_column(sa.Column('scoperto', sa.DECIMAL(10, 2), nullable=True))
        if 'perc_franchigia' not in columns:
            batch_op.add_column(sa.Column('perc_franchigia', sa.DECIMAL(5, 2), nullable=True))
        
        # Create index on sinistro field if it doesn't exist
        try:
            batch_op.create_index(op.f('ix_work_orders_sinistro'), ['sinistro'], unique=False)
        except:
            pass
        
        # Add foreign key constraint if it doesn't exist
        try:
            batch_op.create_foreign_key(
                op.f('fk_work_orders_ramo_sinistro_id_insurance_branch_types'),
                'insurance_branch_types',
                ['ramo_sinistro_id'],
                ['id']
            )
        except:
            pass
        
        # Remove note column from work_orders if it exists
        if 'note' in columns:
            batch_op.drop_column('note')


def downgrade() -> None:
    # SQLite batch mode for schema changes
    with op.batch_alter_table('work_orders', schema=None) as batch_op:
        # Add note column back
        batch_op.add_column(sa.Column('note', sa.Text(), nullable=True))
        
        # Drop index on sinistro
        batch_op.drop_index(op.f('ix_work_orders_sinistro'))
        
        # Drop foreign key
        batch_op.drop_constraint(
            op.f('fk_work_orders_ramo_sinistro_id_insurance_branch_types'),
            type_='foreignkey'
        )
        
        # Drop insurance claim columns from work_orders
        batch_op.drop_column('perc_franchigia')
        batch_op.drop_column('scoperto')
        batch_op.drop_column('compagnia_debitrice_sinistro')
        batch_op.drop_column('compagnia_sinistro')
        batch_op.drop_column('numero_sinistro')
        batch_op.drop_column('autorita')
        batch_op.drop_column('legale')
        batch_op.drop_column('ramo_sinistro_id')
        batch_op.drop_column('sinistro')

    # Drop insurance_branch_types table
    op.drop_index(op.f('ix_insurance_branch_types_codice'), table_name='insurance_branch_types')
    op.drop_index(op.f('ix_insurance_branch_types_nome'), table_name='insurance_branch_types')
    op.drop_table('insurance_branch_types')
