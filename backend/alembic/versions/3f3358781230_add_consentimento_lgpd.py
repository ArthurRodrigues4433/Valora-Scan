"""add consentimento_lgpd

Revision ID: 3f3358781230
Revises: fix_feira_itens_nullable
Create Date: 2026-07-21 13:35:45.948438

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f3358781230'
down_revision: Union[str, Sequence[str], None] = 'fix_feira_itens_nullable'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("notas_fiscais", sa.Column("consentimento_lgpd", sa.Boolean(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
