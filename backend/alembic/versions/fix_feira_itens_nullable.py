"""make feira_itens fields nullable

Revision ID: fix_feira_itens_nullable
Revises: a955e8155282
Create Date: 2026-06-08 18:35:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'fix_feira_itens_nullable'
down_revision: Union[str, Sequence[str], None] = 'a955e8155282'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('''
        ALTER TABLE feira_itens RENAME TO feira_itens_old
    ''')
    op.execute('''
        CREATE TABLE feira_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR NOT NULL,
            categoria VARCHAR,
            preco_varejo DECIMAL(10, 2) NOT NULL,
            preco_atacado DECIMAL(10, 2),
            qtd_minima_atacado INTEGER,
            quantidade INTEGER NOT NULL,
            preco_escolhido DECIMAL(10, 2) NOT NULL,
            subtotal DECIMAL(10, 2) NOT NULL,
            unidade_medida VARCHAR,
            imagem_url VARCHAR,
            ocr_texto VARCHAR,
            created_at DATETIME,
            feira_id INTEGER NOT NULL,
            FOREIGN KEY (feira_id) REFERENCES feiras(id)
        )
    ''')
    op.execute('''
        INSERT INTO feira_itens (id, nome, categoria, preco_varejo, preco_atacado, qtd_minima_atacado, quantidade, preco_escolhido, subtotal, unidade_medida, imagem_url, ocr_texto, created_at, feira_id)
        SELECT id, nome, categoria, preco_varejo, preco_atacado, qtd_minima_atacado, quantidade, preco_escolhido, subtotal, unidade_medida, imagem_url, ocr_texto, created_at, feira_id FROM feira_itens_old
    ''')
    op.execute('DROP TABLE feira_itens_old')


def downgrade() -> None:
    op.execute('''
        ALTER TABLE feira_itens RENAME TO feira_itens_old
    ''')
    op.execute('''
        CREATE TABLE feira_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR NOT NULL,
            categoria VARCHAR,
            preco_varejo DECIMAL(10, 2) NOT NULL,
            preco_atacado DECIMAL(10, 2) NOT NULL,
            qtd_minima_atacado INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_escolhido DECIMAL(10, 2) NOT NULL,
            subtotal DECIMAL(10, 2) NOT NULL,
            unidade_medida VARCHAR NOT NULL,
            imagem_url VARCHAR,
            ocr_texto VARCHAR,
            created_at DATETIME,
            feira_id INTEGER NOT NULL,
            FOREIGN KEY (feira_id) REFERENCES feiras(id)
        )
    ''')
    op.execute('''
        INSERT INTO feira_itens (id, nome, categoria, preco_varejo, preco_atacado, qtd_minima_atacado, quantidade, preco_escolhido, subtotal, unidade_medida, imagem_url, ocr_texto, created_at, feira_id)
        SELECT id, nome, categoria, preco_varejo, preco_atacado, qtd_minima_atacado, quantidade, preco_escolhido, subtotal, unidade_medida, imagem_url, ocr_texto, created_at, feira_id FROM feira_itens_old
    ''')
    op.execute('DROP TABLE feira_itens_old')