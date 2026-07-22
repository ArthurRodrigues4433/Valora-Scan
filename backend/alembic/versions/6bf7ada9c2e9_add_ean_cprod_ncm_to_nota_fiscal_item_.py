"""add ean cprod ncm to nota_fiscal_item and feira_item

Revision ID: 6bf7ada9c2e9
Revises: 8890653996f7
Create Date: 2026-07-22 10:48:42.565873

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bf7ada9c2e9'
down_revision: Union[str, Sequence[str], None] = '8890653996f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('feira_itens', sa.Column('ean', sa.String(), nullable=True))
    op.add_column('feira_itens', sa.Column('cod_interno', sa.String(), nullable=True))
    op.create_index(op.f('ix_feira_itens_cod_interno'), 'feira_itens', ['cod_interno'], unique=False)
    op.create_index(op.f('ix_feira_itens_ean'), 'feira_itens', ['ean'], unique=False)
    op.add_column('nota_fiscal_itens', sa.Column('ean', sa.String(), nullable=True))
    op.add_column('nota_fiscal_itens', sa.Column('cprod', sa.String(), nullable=True))
    op.add_column('nota_fiscal_itens', sa.Column('ncm', sa.String(), nullable=True))
    op.create_index(op.f('ix_nota_fiscal_itens_cprod'), 'nota_fiscal_itens', ['cprod'], unique=False)
    op.create_index(op.f('ix_nota_fiscal_itens_ean'), 'nota_fiscal_itens', ['ean'], unique=False)
    op.create_index(op.f('ix_nota_fiscal_itens_ncm'), 'nota_fiscal_itens', ['ncm'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_nota_fiscal_itens_ncm'), table_name='nota_fiscal_itens')
    op.drop_index(op.f('ix_nota_fiscal_itens_ean'), table_name='nota_fiscal_itens')
    op.drop_index(op.f('ix_nota_fiscal_itens_cprod'), table_name='nota_fiscal_itens')
    op.drop_column('nota_fiscal_itens', 'ncm')
    op.drop_column('nota_fiscal_itens', 'cprod')
    op.drop_column('nota_fiscal_itens', 'ean')
    op.drop_index(op.f('ix_feira_itens_ean'), table_name='feira_itens')
    op.drop_index(op.f('ix_feira_itens_cod_interno'), table_name='feira_itens')
    op.drop_column('feira_itens', 'cod_interno')
    op.drop_column('feira_itens', 'ean')
