"""Add RBAC system - workshops, permissions, role_permissions tables

Revision ID: add_rbac_system
Revises: add_insurance_claims, 3d488bb3ba1b
Create Date: 2026-02-20 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# Revision identifiers, used by Alembic.
revision = 'add_rbac_system'
down_revision = ('add_insurance_claims', '3d488bb3ba1b')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create workshops table
    op.create_table(
        'workshops',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('tipo', sa.String(50), nullable=False),
        sa.Column('responsabile_id', sa.Integer(), nullable=True),
        sa.Column('indirizzo', sa.Text(), nullable=True),
        sa.Column('attivo', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['responsabile_id'], ['users.id'], name='fk_workshops_responsabile_id_users'),
        sa.PrimaryKeyConstraint('id', name='pk_workshops'),
        sa.UniqueConstraint('nome', name='uq_workshops_nome'),
    )
    op.create_index('ix_workshops_nome', 'workshops', ['nome'], unique=True)
    op.create_index('ix_workshops_attivo', 'workshops', ['attivo'], unique=False)
    
    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codice', sa.String(100), nullable=False),
        sa.Column('nome', sa.String(200), nullable=False),
        sa.Column('categoria', sa.String(50), nullable=False),
        sa.Column('descrizione', sa.Text(), nullable=True),
        sa.Column('attivo', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id', name='pk_permissions'),
        sa.UniqueConstraint('codice', name='uq_permissions_codice'),
    )
    op.create_index('ix_permissions_codice', 'permissions', ['codice'], unique=True)
    op.create_index('ix_permissions_categoria', 'permissions', ['categoria'], unique=False)
    op.create_index('ix_permissions_attivo', 'permissions', ['attivo'], unique=False)
    
    # Create role_permissions table
    op.create_table(
        'role_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ruolo', sa.String(50), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('granted', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], name='fk_role_permissions_permission_id_permissions', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_role_permissions_updated_by_users'),
        sa.PrimaryKeyConstraint('id', name='pk_role_permissions'),
        sa.UniqueConstraint('ruolo', 'permission_id', name='uq_role_permission'),
    )
    op.create_index('ix_role_permissions_ruolo', 'role_permissions', ['ruolo'], unique=False)
    
    # Add workshop_id column to users table
    ctx = op.get_context()
    inspector = inspect(ctx.bind)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'workshop_id' not in columns:
        op.add_column('users', sa.Column('workshop_id', sa.Integer(), nullable=True))
        op.create_foreign_key(
            'fk_users_workshop_id_workshops',
            'users', 'workshops',
            ['workshop_id'], ['id']
        )
        op.create_index('ix_users_workshop_id', 'users', ['workshop_id'], unique=False)


def downgrade() -> None:
    # Drop index on users.workshop_id
    op.drop_index('ix_users_workshop_id', table_name='users')
    
    # Drop foreign key on users.workshop_id
    op.drop_constraint('fk_users_workshop_id_workshops', 'users', type_='foreignkey')
    
    # Drop workshop_id column
    op.drop_column('users', 'workshop_id')
    
    # Drop role_permissions table
    op.drop_index('ix_role_permissions_ruolo', table_name='role_permissions')
    op.drop_table('role_permissions')
    
    # Drop permissions table
    op.drop_index('ix_permissions_attivo', table_name='permissions')
    op.drop_index('ix_permissions_categoria', table_name='permissions')
    op.drop_index('ix_permissions_codice', table_name='permissions')
    op.drop_table('permissions')
    
    # Drop workshops table
    op.drop_index('ix_workshops_attivo', table_name='workshops')
    op.drop_index('ix_workshops_nome', table_name='workshops')
    op.drop_table('workshops')
