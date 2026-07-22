"""add_missing_indexes_and_constraints

Revision ID: 5ad72c63ae4c
Revises: 6bf7ada9c2e9
Create Date: 2026-07-22 13:46:05.289393
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5ad72c63ae4c'
down_revision: Union[str, Sequence[str], None] = '6bf7ada9c2e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('feiras') as batch_op:
        batch_op.create_index('ix_feiras_usuario_id_status', ['usuario_id', 'status'], unique=False)

    with op.batch_alter_table('feira_itens') as batch_op:
        batch_op.create_index('ix_feira_itens_feira_id', ['feira_id'], unique=False)

    with op.batch_alter_table('notas_fiscais') as batch_op:
        batch_op.create_index('ix_notas_fiscais_feira_id', ['feira_id'], unique=False)
        batch_op.create_index('ix_notas_fiscais_qr_code', ['qr_code'], unique=True)

    with op.batch_alter_table('nota_fiscal_itens') as batch_op:
        batch_op.create_index('ix_nota_fiscal_itens_nota_fiscal_id', ['nota_fiscal_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('nota_fiscal_itens') as batch_op:
        batch_op.drop_index('ix_nota_fiscal_itens_nota_fiscal_id')

    with op.batch_alter_table('notas_fiscais') as batch_op:
        batch_op.drop_index('ix_notas_fiscais_qr_code')
        batch_op.drop_index('ix_notas_fiscais_feira_id')

    with op.batch_alter_table('feira_itens') as batch_op:
        batch_op.drop_index('ix_feira_itens_feira_id')

    with op.batch_alter_table('feiras') as batch_op:
        batch_op.drop_index('ix_feiras_usuario_id_status')
