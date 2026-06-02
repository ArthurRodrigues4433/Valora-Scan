"""update

Revision ID: a955e8155282
Revises: b33914532ad7
Create Date: 2026-06-01 16:38:44.079467

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a955e8155282'
down_revision: Union[str, Sequence[str], None] = 'b33914532ad7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('''
        CREATE TABLE usuarios_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR NOT NULL,
            email VARCHAR NOT NULL UNIQUE,
            senha VARCHAR NOT NULL,
            ativo BOOLEAN,
            admin BOOLEAN DEFAULT 0
        )
    ''')
    op.execute('''
        INSERT INTO usuarios_new (id, nome, email, senha, ativo, admin)
        SELECT id, nome, email, senha, ativo, admin FROM usuarios
    ''')
    op.execute('DROP TABLE usuarios')
    op.execute('ALTER TABLE usuarios_new RENAME TO usuarios')


def downgrade() -> None:
    op.execute('''
        CREATE TABLE usuarios_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR,
            email VARCHAR NOT NULL UNIQUE,
            senha VARCHAR,
            ativo BOOLEAN,
            admin BOOLEAN DEFAULT 0
        )
    ''')
    op.execute('''
        INSERT INTO usuarios_new (id, nome, email, senha, ativo, admin)
        SELECT id, nome, email, senha, ativo, admin FROM usuarios
    ''')
    op.execute('DROP TABLE usuarios')
    op.execute('ALTER TABLE usuarios_new RENAME TO usuarios')
