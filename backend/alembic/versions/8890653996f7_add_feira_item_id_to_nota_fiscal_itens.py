"""add feira_item_id to nota_fiscal_itens

Revision ID: 8890653996f7
Revises: 3f3358781230
Create Date: 2026-07-21 14:02:34.044099

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8890653996f7'
down_revision: Union[str, Sequence[str], None] = '3f3358781230'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("nota_fiscal_itens", sa.Column("feira_item_id", sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("nota_fiscal_itens", "feira_item_id")
