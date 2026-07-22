from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class NotaFiscalItem(Base):
    __tablename__ = "nota_fiscal_itens"

    id = Column(Integer, primary_key=True, index=True)
    produto_nome = Column(String, nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(DECIMAL(10, 2), nullable=False)
    preco_total = Column(DECIMAL(10, 2), nullable=False)
    divergencia = Column(Boolean, default=False, nullable=False)
    valor_esperado = Column(DECIMAL(10, 2), nullable=True)
    diferenca = Column(DECIMAL(10, 2), nullable=True)
    ean = Column(String, nullable=True, index=True)
    cprod = Column(String, nullable=True, index=True)
    ncm = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    nota_fiscal_id = Column(Integer, ForeignKey("notas_fiscais.id"), nullable=False)
    feira_item_id = Column(Integer, ForeignKey("feira_itens.id"), nullable=True)

    nota_fiscal = relationship("NotaFiscal", back_populates="nota_fiscal_itens")