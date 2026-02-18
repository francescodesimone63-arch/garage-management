"""add_intervention_status_types_and_update_interventions

Revision ID: 7c28deedac76
Revises: f6g7h8i9j0k1
Create Date: 2026-02-16 13:17:34.304435+01:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c28deedac76'
down_revision: Union[str, None] = 'f6g7h8i9j0k1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Aggiungi colonne una per una
    op.add_column('interventions', sa.Column('data_inizio', sa.DateTime(), nullable=True))
    op.add_column('interventions', sa.Column('data_fine', sa.DateTime(), nullable=True))
    op.add_column('interventions', sa.Column('ore_effettive', sa.Float(), nullable=True))
    op.add_column('interventions', sa.Column('note_intervento', sa.Text(), nullable=True))
    op.add_column('interventions', sa.Column('note_sospensione', sa.Text(), nullable=True))
    
    # Modifica colonne esistenti (una per volta)
    op.alter_column('interventions', 'created_at', nullable=False)
    op.alter_column('interventions', 'updated_at', nullable=False)
    
    # Crea enum/tabella status
    op.create_table('intervention_status_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column('interventions', sa.Column('status_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'interventions', 'intervention_status_types', 
                         ['status_id'], ['id'])

def downgrade():
    # Reverse operations
    op.drop_column('interventions', 'status_id')
    op.drop_table('intervention_status_types')
    op.drop_column('interventions', 'note_sospensione')
    op.drop_column('interventions', 'note_intervento')
    op.drop_column('interventions', 'stato_intervento_id')
    op.drop_index(op.f('ix_intervention_status_types_id'), table_name='intervention_status_types')
    op.drop_index(op.f('ix_intervention_status_types_codice'), table_name='intervention_status_types')
    op.drop_table('intervention_status_types')
    # ### end Alembic commands ###
